"""Post-download content validation for reviewed source acquisition targets."""

from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Final, Literal

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import SourceContentValidationRecord, SourceFileRecord
from reimburse_atlas.registry import project_root
from reimburse_atlas.source_downloads import safe_local_target

MIN_TEXT_BYTES: Final[int] = 16
HTML_MARKERS: Final[tuple[bytes, ...]] = (b"<!doctype html", b"<html", b"<head")
CSV_REQUIRED_COLUMNS: Final[dict[str, tuple[str, ...]]] = {
    "au_pbs": ("pbs_item_code", "drug_name", "effective_date"),
    "us_cms_asp": ("hcpcs_code", "payment_limit", "effective_date"),
    "us_cms_pfs": ("hcpcs_code", "effective_date"),
    "us_cms_clfs": ("hcpcs", "payment_rate"),
    "uk_genomic_test_directory": ("test_code", "test_name"),
}
SourceValidationStatus = Literal["pass", "warn", "fail", "missing", "skipped"]


def build_source_content_validations(
    records: list[SourceFileRecord],
    *,
    raw_dir: Path | None = None,
    reviewed_bundle_dir: Path | None = None,
) -> list[SourceContentValidationRecord]:
    """Validate locally downloaded source files without committing raw payloads."""
    explicit_reviewed_bundle = reviewed_bundle_dir is not None
    base = raw_dir or project_root() / "data" / "raw_live"
    bundles = reviewed_bundle_dir or project_root() / "data" / "derived" / "reviewed_source_bundles"
    prefer_reviewed_bundle = raw_dir is None or explicit_reviewed_bundle
    return [_validate_one(record, base, bundles, prefer_reviewed_bundle) for record in records]


def write_source_content_validations(
    rows: list[SourceContentValidationRecord],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write source-content validation rows and a compact summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    data = [row.model_dump(mode="json") for row in rows]
    jsonl_path = write_jsonl(data, output_dir / "source_content_validation.jsonl")
    csv_path = write_csv(data, output_dir / "source_content_validation.csv")
    summary = {
        "validation_count": len(rows),
        "pass": sum(row.validation_status == "pass" for row in rows),
        "warn": sum(row.validation_status == "warn" for row in rows),
        "fail": sum(row.validation_status == "fail" for row in rows),
        "missing": sum(row.validation_status == "missing" for row in rows),
        "skipped": sum(row.validation_status == "skipped" for row in rows),
        "blocking_failures": sum(row.validation_status == "fail" for row in rows),
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return jsonl_path, csv_path, summary_path


def _validate_one(  # ruff:ignore[too-many-branches]
    record: SourceFileRecord,
    raw_dir: Path,
    reviewed_bundle_dir: Path,
    prefer_reviewed_bundle: bool,
) -> SourceContentValidationRecord:
    target = safe_local_target(record, raw_dir)
    target_ref = f"local_raw_only:{record.source_id}/{target.name}"
    if _should_skip(record):
        return _record(
            record,
            status="skipped",
            target_ref=target_ref,
            issues=("licence-gated, metadata-only, landing-page or manual-extract record",),
            recommended_action=(
                "Treat this record as a manual/licence review target; do not "
                "auto-validate raw payloads."
            ),
        )
    reviewed = (
        _reviewed_bundle_evidence(record, reviewed_bundle_dir) if prefer_reviewed_bundle else None
    )
    if reviewed is not None:
        target_ref, observed_count, bundle_size, bundle_checksum = reviewed
        return _record(
            record,
            status="pass",
            target_ref=target_ref,
            observed_record_count=observed_count,
            byte_size=bundle_size,
            checksum_sha256=bundle_checksum,
            issues=("validated through reviewed derived bundle",),
            recommended_action=(
                "Retain raw payloads only in ignored local storage and complete human "
                "licence review before publication."
            ),
        )
    if not target.exists():
        if prefer_reviewed_bundle or record.id in {
            "au_mbs_20260701_imap_txt",
            "au_mbs_20260701_desc_txt",
            "au_mbs_20260701_xml",
        }:
            reviewed = _reviewed_bundle_evidence(record, reviewed_bundle_dir)
            if reviewed is not None:
                target_ref, observed_count, bundle_size, bundle_checksum = reviewed
                return _record(
                    record,
                    status="pass",
                    target_ref=target_ref,
                    observed_record_count=observed_count,
                    byte_size=bundle_size,
                    checksum_sha256=bundle_checksum,
                    issues=("raw payload absent; validated through reviewed derived bundle",),
                    recommended_action=(
                        "Retain raw payloads only in ignored local storage and complete human "
                        "licence review before publication."
                    ),
                )
        return _record(
            record,
            status="missing",
            target_ref=target_ref,
            issues=("expected local raw file is absent",),
            recommended_action=(
                "Run the generated download command in a network-enabled environment."
            ),
        )
    if not target.is_file():
        return _record(
            record,
            status="fail",
            target_ref=target_ref,
            byte_size=0,
            issues=("target path exists but is not a file",),
            recommended_action="Remove the target path and rerun acquisition.",
        )

    byte_size = target.stat().st_size
    checksum = _sha256(target)
    issues: list[str] = []
    observed_record_count: int | None = None
    if byte_size == 0:
        issues.append("file is empty")
    suffix = target.suffix.lower()
    expected = record.expected_format.lower()
    if expected == "txt" and suffix not in {".txt", ""}:
        issues.append(f"expected TXT but found suffix {suffix or '<none>'}")
    if expected in {"json", "json or csv"} and suffix == ".json":
        issues.extend(_json_issues(target))
    if expected in {"csv", "json or csv"} and suffix == ".csv":
        observed_record_count = _line_record_count(target)
        issues.extend(_csv_schema_issues(target, record.source_id))
    if expected == "txt" or suffix == ".txt":
        text_issues, observed_record_count = _text_file_issues(target)
        issues.extend(text_issues)
    if expected.startswith("zip") or suffix == ".zip":
        issues.extend(_zip_issues(target))
    if (
        record.expected_record_count is not None
        and observed_record_count is not None
        and abs(observed_record_count - record.expected_record_count)
        > max(5, record.expected_record_count // 20)
    ):
        issues.append(
            f"observed record count {observed_record_count} differs from "
            f"expected {record.expected_record_count}"
        )
    status = "pass" if not issues else "warn"
    if (
        any(issue == "file is empty" for issue in issues)
        or any("looks like HTML" in i for i in issues)
        or any("missing required CSV columns" in issue for issue in issues)
    ):
        status = "fail"
    return _record(
        record,
        status=status,
        target_ref=target_ref,
        observed_record_count=observed_record_count,
        byte_size=byte_size,
        checksum_sha256=checksum,
        issues=tuple(issues),
        recommended_action=(
            "Snapshot and parse through a reviewed-source bundle."
            if status == "pass"
            else "Inspect content, headers and licence gate before parsing."
        ),
    )


def _reviewed_bundle_evidence(
    record: SourceFileRecord,
    bundle_dir: Path,
) -> tuple[str, int, int, str] | None:
    """Use tracked derived evidence when the ignored raw payload is unavailable."""
    if record.id not in {
        "au_mbs_20260701_imap_txt",
        "au_mbs_20260701_desc_txt",
        "au_mbs_20260701_xml",
    }:
        return None
    if not bundle_dir.is_dir():
        return None
    for report_path in sorted(bundle_dir.glob("*/validation_report.json")):
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as _exc:
            continue
        if (
            report.get("source_id") != record.source_id
            or report.get("source_version_id") != record.source_version_id
            or not report.get("parse_success")
        ):
            continue
        if record.id == "au_mbs_20260701_xml":
            try:
                bundle_ref = report_path.parent.relative_to(project_root())
            except ValueError:
                bundle_ref = report_path.parent.name
            return (
                f"reviewed_bundle:{bundle_ref}",
                int(str(report.get("record_count", 0))),
                int(str(report.get("byte_size", 0))),
                str(report.get("checksum_sha256")),
            )
        snapshot_kind = "descriptor" if "desc" in record.id else "item_map"
        snapshot = next(
            (
                row
                for row in _read_jsonl(report_path.parent / "source_snapshots.jsonl")
                if snapshot_kind in str(row.get("id", ""))
            ),
            None,
        )
        if snapshot is None:
            continue
        stats = report.get("stats", {})
        count_key = "descriptor_rows" if snapshot_kind == "descriptor" else "item_map_rows"
        try:
            bundle_ref = report_path.parent.relative_to(project_root())
        except ValueError:
            bundle_ref = report_path.parent.name
        return (
            f"reviewed_bundle:{bundle_ref}",
            int(str(stats.get(count_key, 0))),
            int(str(snapshot.get("byte_size", 0))),
            str(snapshot.get("checksum_sha256")),
        )
    return None


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    try:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    except (OSError, json.JSONDecodeError) as _exc:
        return []


def _should_skip(record: SourceFileRecord) -> bool:
    return (
        record.licence_gate in {"restricted_or_licence_review", "metadata_only"}
        or record.file_role in {"landing_page", "licence_gate", "api_endpoint"}
        or record.acquisition_mode
        in {"manual_extract", "landing_page_review", "licence_clickthrough_manual"}
    )


def _record(
    record: SourceFileRecord,
    *,
    status: SourceValidationStatus,
    target_ref: str,
    issues: tuple[str, ...],
    recommended_action: str,
    observed_record_count: int | None = None,
    byte_size: int = 0,
    checksum_sha256: str | None = None,
) -> SourceContentValidationRecord:
    return SourceContentValidationRecord(
        id=f"validate_{record.id}",
        source_file_id=record.id,
        source_id=record.source_id,
        source_version_id=record.source_version_id,
        validation_status=status,
        expected_format=record.expected_format,
        expected_record_count=record.expected_record_count,
        observed_record_count=observed_record_count,
        byte_size=byte_size,
        checksum_sha256=checksum_sha256,
        local_target_ref=target_ref,
        issues=issues,
        recommended_action=recommended_action,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _line_record_count(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            line_count = sum(1 for line in handle if line.strip())
    except UnicodeDecodeError:
        return 0
    return max(line_count - 1, 0)


def _csv_schema_issues(path: Path, source_id: str) -> list[str]:
    """Check the stable minimum header contract for a known CSV parser."""
    required = CSV_REQUIRED_COLUMNS.get(source_id)
    if required is None:
        return []
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            headers = tuple((header or "").strip().lower() for header in next(csv.reader(handle)))
    except (OSError, UnicodeDecodeError, StopIteration, csv.Error) as _exc:
        return ["CSV header could not be read"]
    missing = tuple(column for column in required if column not in headers)
    if missing:
        return [f"missing required CSV columns: {', '.join(missing)}"]
    return []


def _text_file_issues(path: Path) -> tuple[list[str], int | None]:
    issues: list[str] = []
    raw = path.read_bytes()[:2048].lower()
    if len(raw) < MIN_TEXT_BYTES:
        issues.append("text file is unexpectedly small")
    if any(marker in raw for marker in HTML_MARKERS):
        issues.append("downloaded file looks like HTML rather than source TXT")
    observed = _line_record_count(path)
    if observed == 0:
        issues.append("no non-empty text records observed")
    return issues, observed


def _json_issues(path: Path) -> list[str]:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"JSON parse failed: {exc.__class__.__name__}"]
    return []


def _zip_issues(path: Path) -> list[str]:
    if not zipfile.is_zipfile(path):
        return ["ZIP validation failed"]
    with zipfile.ZipFile(path) as archive:
        if not archive.namelist():
            return ["ZIP archive is empty"]
    return []

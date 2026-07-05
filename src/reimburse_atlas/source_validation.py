"""Post-download content validation for reviewed source acquisition targets."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Final

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import SourceContentValidationRecord, SourceFileRecord
from reimburse_atlas.registry import project_root
from reimburse_atlas.source_downloads import safe_local_target

MIN_TEXT_BYTES: Final[int] = 16
HTML_MARKERS: Final[tuple[bytes, ...]] = (b"<!doctype html", b"<html", b"<head")


def build_source_content_validations(
    records: list[SourceFileRecord],
    *,
    raw_dir: Path | None = None,
) -> list[SourceContentValidationRecord]:
    """Validate locally downloaded source files without committing raw payloads."""
    base = raw_dir or project_root() / "data" / "raw_live"
    return [_validate_one(record, base) for record in records]


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


def _validate_one(record: SourceFileRecord, raw_dir: Path) -> SourceContentValidationRecord:
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
    if not target.exists():
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
    if any(issue == "file is empty" for issue in issues) or any(
        "looks like HTML" in i for i in issues
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


def _should_skip(record: SourceFileRecord) -> bool:
    return (
        record.licence_gate in {"restricted_or_licence_review", "metadata_only"}
        or record.file_role in {"landing_page", "licence_gate"}
        or record.acquisition_mode
        in {"manual_extract", "landing_page_review", "licence_clickthrough_manual"}
    )


def _record(
    record: SourceFileRecord,
    *,
    status: str,
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

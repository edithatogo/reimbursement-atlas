"""Local-source validation utilities.

These helpers are the bridge between design fixtures and reviewed live-source
files. They deliberately do not fetch data from the network. A maintainer
manually downloads a public file, places it in an ignored local raw cache, then
uses these functions to create checksum provenance and derived-only outputs.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, cast

from reimburse_atlas.contracts import (
    CoverageDecisionRecord,
    ScheduleItemRecord,
    SourceSnapshotRecord,
)
from reimburse_atlas.io import pydantic_rows, write_csv, write_jsonl
from reimburse_atlas.parsers import (
    parse_cms_asp_csv,
    parse_cms_clfs_csv,
    parse_cms_pfs_csv,
    parse_mbs_xml,
    parse_nhs_genomic_directory_csv,
    parse_pbs_csv,
)
from reimburse_atlas.parsers.mbs_txt import MbsTxtParseStats, parse_mbs_txt_pair, parse_stats
from reimburse_atlas.registry import load_source_versions
from reimburse_atlas.snapshots import file_sha256, write_snapshot_records

ParsedRecord = ScheduleItemRecord | CoverageDecisionRecord
Parser = Callable[[Path], list[ParsedRecord]]

PARSER_BY_SOURCE_ID: dict[str, Parser] = {
    "au_mbs": cast("Parser", parse_mbs_xml),
    "au_pbs": cast("Parser", parse_pbs_csv),
    "us_cms_asp": cast("Parser", parse_cms_asp_csv),
    "us_cms_clfs": cast("Parser", parse_cms_clfs_csv),
    "us_cms_pfs": cast("Parser", parse_cms_pfs_csv),
    "uk_genomic_test_directory": cast("Parser", parse_nhs_genomic_directory_csv),
}


@dataclass(frozen=True)
class LocalParseResult:
    """Metadata returned after parsing a reviewed local source file."""

    source_id: str
    source_version_id: str
    record_type: Literal["schedule_items", "coverage_decisions"]
    record_count: int
    jsonl_path: Path
    csv_path: Path


@dataclass(frozen=True)
class ReviewedSourceBundleResult:
    """Metadata returned after building a reviewed local source package."""

    source_id: str
    source_version_id: str
    snapshot_id: str
    record_type: Literal["schedule_items", "coverage_decisions"]
    record_count: int
    bundle_dir: Path
    snapshot_jsonl_path: Path
    parsed_jsonl_path: Path
    parsed_csv_path: Path
    validation_report_path: Path
    publication_manifest_path: Path


def version_source_id(source_version_id: str) -> str:
    """Return the parent source id for a source version."""
    versions = {version.id: version for version in load_source_versions()}
    if source_version_id not in versions:
        msg = f"Unknown source version id: {source_version_id}"
        raise KeyError(msg)
    return versions[source_version_id].source_id


def snapshot_reviewed_local_file(
    *,
    source_version_id: str,
    path: Path,
    content_type: str,
    retrieved_at: str | None = None,
    licence_gate: Literal[
        "permissive",
        "public_reuse_review",
        "restricted_local_only",
    ] = "public_reuse_review",
    cache_scope: Literal[
        "public_raw_cache",
        "public_derived_only",
        "local_raw_only",
        "metadata_only",
    ] = "public_derived_only",
    notes: str | None = None,
) -> SourceSnapshotRecord:
    """Build a snapshot record for a manually downloaded local source file."""
    versions = {version.id: version for version in load_source_versions()}
    if source_version_id not in versions:
        msg = f"Unknown source version id: {source_version_id}"
        raise KeyError(msg)
    version = versions[source_version_id]
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        msg = f"Local source file not found: {resolved}"
        raise FileNotFoundError(msg)
    timestamp = retrieved_at or _metadata_retrieved_at(resolved) or datetime.now(tz=UTC).isoformat()
    checksum = file_sha256(resolved)
    return SourceSnapshotRecord(
        id=f"snapshot_{source_version_id}_{checksum[:12]}",
        source_id=version.source_id,
        source_version_id=source_version_id,
        source_url=version.source_url,
        local_path=str(resolved),
        retrieved_at=timestamp,
        content_type=content_type,
        byte_size=resolved.stat().st_size,
        checksum_sha256=checksum,
        licence_gate=licence_gate,
        cache_scope=cache_scope,
        notes=notes or "Reviewed local source snapshot; raw file is not committed by default.",
    )


def parse_reviewed_local_file(
    *,
    source_version_id: str,
    path: Path,
    output_dir: Path,
) -> LocalParseResult:
    """Parse a manually downloaded local source file into derived contract rows."""
    source_id = version_source_id(source_version_id)
    parser = PARSER_BY_SOURCE_ID.get(source_id)
    if parser is None:
        msg = f"No parser registered for source id: {source_id}"
        raise KeyError(msg)
    records = parser(path.expanduser().resolve())
    record_type = _record_type(records)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = pydantic_rows(list(records))
    stem = f"{source_version_id}_{record_type}"
    jsonl_path = write_jsonl(rows, output_dir / f"{stem}.jsonl")
    csv_path = write_csv(rows, output_dir / f"{stem}.csv")
    return LocalParseResult(
        source_id=source_id,
        source_version_id=source_version_id,
        record_type=record_type,
        record_count=len(records),
        jsonl_path=jsonl_path,
        csv_path=csv_path,
    )


def build_reviewed_source_bundle(
    *,
    source_version_id: str,
    path: Path,
    content_type: str,
    output_dir: Path,
    retrieved_at: str | None = None,
    licence_gate: Literal[
        "permissive",
        "public_reuse_review",
        "restricted_local_only",
    ] = "public_reuse_review",
    cache_scope: Literal[
        "public_raw_cache",
        "public_derived_only",
        "local_raw_only",
        "metadata_only",
    ] = "local_raw_only",
) -> ReviewedSourceBundleResult:
    """Snapshot, parse and report on one reviewed local source file.

    The raw file remains wherever the caller placed it. The bundle contains only
    checksum metadata, derived normalised rows and a publication-manifest draft.
    """
    snapshot = snapshot_reviewed_local_file(
        source_version_id=source_version_id,
        path=path,
        content_type=content_type,
        retrieved_at=retrieved_at,
        licence_gate=licence_gate,
        cache_scope=cache_scope,
        notes="Reviewed local source bundle metadata; raw file is not copied into the bundle.",
    )
    bundle_dir = output_dir / snapshot.id
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle_snapshot = _redact_snapshot_local_path(snapshot)
    snapshot_jsonl, _snapshot_csv = write_snapshot_records([bundle_snapshot], bundle_dir)
    parse_result = parse_reviewed_local_file(
        source_version_id=source_version_id,
        path=path,
        output_dir=bundle_dir,
    )
    validation_report_path = _write_validation_report(
        bundle_dir=bundle_dir,
        snapshot=snapshot,
        parse_result=parse_result,
    )
    # build_publication_manifest is repo-relative by default; local bundles can sit anywhere.
    # Therefore write a minimal bundle-local publication manifest directly.
    publication_manifest_path = bundle_dir / "publication_manifest.json"
    publication_manifest_path.write_text(
        json.dumps(
            {
                "project": "reimbursement-atlas-conductor",
                "manifest_version": "reviewed-source-bundle-v1",
                "source_id": snapshot.source_id,
                "source_version_id": source_version_id,
                "snapshot_id": snapshot.id,
                "raw_file_copied": False,
                "raw_cache_scope": snapshot.cache_scope,
                "derived_files": [
                    parse_result.jsonl_path.name,
                    parse_result.csv_path.name,
                    snapshot_jsonl.name,
                    validation_report_path.name,
                ],
                "licence_gate": snapshot.licence_gate,
                "record_count": parse_result.record_count,
                "warnings": [
                    "Confirm source-specific redistribution terms before publishing derived rows.",
                    (
                        "Do not publish raw local_path values if they expose private "
                        "filesystem locations."
                    ),
                ],
            },
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )
    return ReviewedSourceBundleResult(
        source_id=snapshot.source_id,
        source_version_id=source_version_id,
        snapshot_id=snapshot.id,
        record_type=parse_result.record_type,
        record_count=parse_result.record_count,
        bundle_dir=bundle_dir,
        snapshot_jsonl_path=snapshot_jsonl,
        parsed_jsonl_path=parse_result.jsonl_path,
        parsed_csv_path=parse_result.csv_path,
        validation_report_path=validation_report_path,
        publication_manifest_path=publication_manifest_path,
    )


def _redact_snapshot_local_path(snapshot: SourceSnapshotRecord) -> SourceSnapshotRecord:
    """Return a bundle-safe snapshot record without private local raw paths."""
    return snapshot.model_copy(
        update={
            "local_path": None,
            "notes": (
                f"{snapshot.notes or 'Reviewed local snapshot.'} "
                "Local raw path redacted for derived bundle publication safety."
            ),
        }
    )


def _write_validation_report(
    *,
    bundle_dir: Path,
    snapshot: SourceSnapshotRecord,
    parse_result: LocalParseResult,
) -> Path:
    """Write a small JSON validation report for a reviewed source bundle."""
    report = {
        "source_id": snapshot.source_id,
        "source_version_id": snapshot.source_version_id,
        "snapshot_id": snapshot.id,
        "checksum_sha256": snapshot.checksum_sha256,
        "byte_size": snapshot.byte_size,
        "record_type": parse_result.record_type,
        "record_count": parse_result.record_count,
        "parse_success": True,
        "raw_file_copied_to_bundle": False,
        "cache_scope": snapshot.cache_scope,
        "licence_gate": snapshot.licence_gate,
        "review_required_before_publication": snapshot.licence_gate != "permissive",
    }
    path = bundle_dir / "validation_report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _record_type(
    records: Sequence[ParsedRecord],
) -> Literal["schedule_items", "coverage_decisions"]:
    """Infer the output table family from parsed records."""
    if not records:
        return "schedule_items"
    first = records[0]
    if isinstance(first, CoverageDecisionRecord):
        return "coverage_decisions"
    return "schedule_items"


@dataclass(frozen=True)
class MbsTxtPairBundleResult:
    """Metadata returned after building a reviewed MBS TXT-pair bundle."""

    source_id: str
    source_version_id: str
    bundle_id: str
    record_type: Literal["schedule_items"]
    record_count: int
    item_map_snapshot_id: str
    descriptor_snapshot_id: str
    bundle_dir: Path
    snapshot_jsonl_path: Path
    parsed_jsonl_path: Path
    parsed_csv_path: Path
    validation_report_path: Path
    publication_manifest_path: Path


def build_mbs_txt_pair_bundle(
    *,
    item_map_path: Path,
    descriptor_path: Path,
    output_dir: Path,
    source_version_id: str = "au_mbs_20260701_txt_pair",
    retrieved_at: str | None = None,
    licence_gate: Literal[
        "permissive",
        "public_reuse_review",
        "restricted_local_only",
    ] = "public_reuse_review",
    cache_scope: Literal[
        "public_raw_cache",
        "public_derived_only",
        "local_raw_only",
        "metadata_only",
    ] = "local_raw_only",
) -> MbsTxtPairBundleResult:
    """Snapshot, parse and report on the two-file MBS TXT source pattern.

    Unlike one-file parsers, current MBS TXT validation needs both an item-map
    file and a descriptor file. The returned bundle contains only derived rows,
    checksum metadata and validation reports; raw TXT files stay in the caller's
    ignored local cache.
    """
    item_map_snapshot = _snapshot_reviewed_pair_file(
        source_version_id=source_version_id,
        path=item_map_path,
        content_type="text/plain",
        role="item_map",
        retrieved_at=retrieved_at,
        licence_gate=licence_gate,
        cache_scope=cache_scope,
    )
    descriptor_snapshot = _snapshot_reviewed_pair_file(
        source_version_id=source_version_id,
        path=descriptor_path,
        content_type="text/plain",
        role="descriptor",
        retrieved_at=retrieved_at,
        licence_gate=licence_gate,
        cache_scope=cache_scope,
    )
    bundle_id = _pair_bundle_id(item_map_snapshot, descriptor_snapshot)
    bundle_dir = output_dir / bundle_id
    bundle_dir.mkdir(parents=True, exist_ok=True)
    snapshot_jsonl, _snapshot_csv = write_snapshot_records(
        [
            _redact_snapshot_local_path(item_map_snapshot),
            _redact_snapshot_local_path(descriptor_snapshot),
        ],
        bundle_dir,
    )
    records = parse_mbs_txt_pair(
        item_map_path.expanduser().resolve(),
        descriptor_path.expanduser().resolve(),
    )
    rows = pydantic_rows(records)
    parsed_jsonl = write_jsonl(rows, bundle_dir / "au_mbs_20260701_txt_pair_schedule_items.jsonl")
    parsed_csv = write_csv(rows, bundle_dir / "au_mbs_20260701_txt_pair_schedule_items.csv")
    stats = parse_stats(
        item_map_path.expanduser().resolve(),
        descriptor_path.expanduser().resolve(),
    )
    validation_report_path = _write_mbs_pair_validation_report(
        bundle_dir=bundle_dir,
        item_map_snapshot=item_map_snapshot,
        descriptor_snapshot=descriptor_snapshot,
        record_count=len(records),
        stats=stats,
    )
    publication_manifest_path = _write_mbs_pair_publication_manifest(
        bundle_dir=bundle_dir,
        bundle_id=bundle_id,
        item_map_snapshot=item_map_snapshot,
        descriptor_snapshot=descriptor_snapshot,
        parsed_jsonl=parsed_jsonl,
        parsed_csv=parsed_csv,
        snapshot_jsonl=snapshot_jsonl,
        validation_report_path=validation_report_path,
        record_count=len(records),
    )
    return MbsTxtPairBundleResult(
        source_id="au_mbs",
        source_version_id=source_version_id,
        bundle_id=bundle_id,
        record_type="schedule_items",
        record_count=len(records),
        item_map_snapshot_id=item_map_snapshot.id,
        descriptor_snapshot_id=descriptor_snapshot.id,
        bundle_dir=bundle_dir,
        snapshot_jsonl_path=snapshot_jsonl,
        parsed_jsonl_path=parsed_jsonl,
        parsed_csv_path=parsed_csv,
        validation_report_path=validation_report_path,
        publication_manifest_path=publication_manifest_path,
    )


def _snapshot_reviewed_pair_file(
    *,
    source_version_id: str,
    path: Path,
    content_type: str,
    role: Literal["item_map", "descriptor"],
    retrieved_at: str | None,
    licence_gate: Literal[
        "permissive",
        "public_reuse_review",
        "restricted_local_only",
    ],
    cache_scope: Literal[
        "public_raw_cache",
        "public_derived_only",
        "local_raw_only",
        "metadata_only",
    ],
) -> SourceSnapshotRecord:
    source_id = version_source_id(source_version_id)
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        msg = f"Local MBS {role} file not found: {resolved}"
        raise FileNotFoundError(msg)
    checksum = file_sha256(resolved)
    versions = {version.id: version for version in load_source_versions()}
    timestamp = retrieved_at or _metadata_retrieved_at(resolved) or datetime.now(tz=UTC).isoformat()
    return SourceSnapshotRecord(
        id=f"snapshot_{source_version_id}_{role}_{checksum[:12]}",
        source_id=source_id,
        source_version_id=source_version_id,
        source_url=versions[source_version_id].source_url,
        local_path=str(resolved),
        retrieved_at=timestamp,
        content_type=content_type,
        byte_size=resolved.stat().st_size,
        checksum_sha256=checksum,
        licence_gate=licence_gate,
        cache_scope=cache_scope,
        notes=(
            f"Reviewed local MBS {role.replace('_', ' ')} snapshot; raw TXT file is "
            "not copied into the derived bundle."
        ),
    )


def _pair_bundle_id(
    item_map_snapshot: SourceSnapshotRecord,
    descriptor_snapshot: SourceSnapshotRecord,
) -> str:
    return (
        f"bundle_{item_map_snapshot.source_version_id}_"
        f"{(item_map_snapshot.checksum_sha256 or '')[:8]}"
        f"{(descriptor_snapshot.checksum_sha256 or '')[:8]}"
    )


def _metadata_retrieved_at(path: Path) -> str | None:
    """Use a download sidecar timestamp when available for reproducible snapshots."""
    metadata_path = path.with_name(path.name + ".metadata.json")
    if not metadata_path.is_file():
        return None
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    typed_metadata = cast("dict[str, object]", metadata) if isinstance(metadata, dict) else {}
    attempted_at = typed_metadata.get("attempted_at")
    return attempted_at if isinstance(attempted_at, str) and attempted_at else None


def _write_mbs_pair_validation_report(
    *,
    bundle_dir: Path,
    item_map_snapshot: SourceSnapshotRecord,
    descriptor_snapshot: SourceSnapshotRecord,
    record_count: int,
    stats: MbsTxtParseStats,
) -> Path:
    stats_payload = asdict(stats)
    report = {
        "source_id": item_map_snapshot.source_id,
        "source_version_id": item_map_snapshot.source_version_id,
        "item_map_snapshot_id": item_map_snapshot.id,
        "descriptor_snapshot_id": descriptor_snapshot.id,
        "item_map_checksum_sha256": item_map_snapshot.checksum_sha256,
        "descriptor_checksum_sha256": descriptor_snapshot.checksum_sha256,
        "record_type": "schedule_items",
        "record_count": record_count,
        "parse_success": True,
        "raw_files_copied_to_bundle": False,
        "cache_scope": item_map_snapshot.cache_scope,
        "licence_gate": item_map_snapshot.licence_gate,
        "stats": stats_payload,
        "review_required_before_publication": item_map_snapshot.licence_gate != "permissive",
        "quality_warnings": _mbs_pair_quality_warnings(stats_payload, record_count),
    }
    path = bundle_dir / "validation_report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _mbs_pair_quality_warnings(stats_payload: dict[str, int], record_count: int) -> list[str]:
    warnings: list[str] = []
    if stats_payload["item_map_rows"] == 0:
        warnings.append("Item-map file produced no rows.")
    if stats_payload["descriptor_rows"] == 0:
        warnings.append("Descriptor file produced no rows.")
    if stats_payload["joined_rows"] == 0 and record_count > 0:
        warnings.append("No item-map rows joined to descriptor rows; inspect MBS code parsing.")
    if stats_payload["descriptor_only_rows"] > 0:
        warnings.append("Descriptor-only rows exist and have no payment amount from the item map.")
    return warnings


def _write_mbs_pair_publication_manifest(
    *,
    bundle_dir: Path,
    bundle_id: str,
    item_map_snapshot: SourceSnapshotRecord,
    descriptor_snapshot: SourceSnapshotRecord,
    parsed_jsonl: Path,
    parsed_csv: Path,
    snapshot_jsonl: Path,
    validation_report_path: Path,
    record_count: int,
) -> Path:
    path = bundle_dir / "publication_manifest.json"
    path.write_text(
        json.dumps(
            {
                "project": "reimbursement-atlas-conductor",
                "manifest_version": "reviewed-source-mbs-txt-pair-bundle-v1",
                "bundle_id": bundle_id,
                "source_id": item_map_snapshot.source_id,
                "source_version_id": item_map_snapshot.source_version_id,
                "raw_files_copied": False,
                "raw_cache_scope": item_map_snapshot.cache_scope,
                "snapshot_ids": [item_map_snapshot.id, descriptor_snapshot.id],
                "derived_files": [
                    parsed_jsonl.name,
                    parsed_csv.name,
                    snapshot_jsonl.name,
                    validation_report_path.name,
                ],
                "licence_gate": item_map_snapshot.licence_gate,
                "record_count": record_count,
                "warnings": [
                    "Confirm MBS reuse terms before publishing derived row sets.",
                    (
                        "Do not publish raw local_path values if they expose private "
                        "filesystem locations."
                    ),
                    (
                        "These derived rows are general-information evidence, not legal "
                        "Medicare benefits rules."
                    ),
                ],
            },
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )
    return path

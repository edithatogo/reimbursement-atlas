"""Snapshot helpers for local fixture and reviewed source-file provenance."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import HttpUrl

from reimburse_atlas.contracts import SourceSnapshotRecord
from reimburse_atlas.registry import load_source_versions, project_root

FIXTURE_SNAPSHOT_TARGETS = {
    "au_mbs_seed_fixture": ("au_mbs", "tests/fixtures/mbs_fragment.xml", "application/xml"),
    "au_pbs_seed_fixture": ("au_pbs", "tests/fixtures/pbs_fixture.csv", "text/csv"),
    "us_cms_asp_seed_fixture": ("us_cms_asp", "tests/fixtures/cms_asp_fixture.csv", "text/csv"),
    "us_cms_clfs_seed_fixture": ("us_cms_clfs", "tests/fixtures/cms_clfs_fixture.csv", "text/csv"),
    "us_cms_pfs_seed_fixture": ("us_cms_pfs", "tests/fixtures/cms_pfs_fixture.csv", "text/csv"),
    "uk_genomic_directory_seed_fixture": (
        "uk_genomic_test_directory",
        "tests/fixtures/nhs_genomic_directory_fixture.csv",
        "text/csv",
    ),
}


def file_sha256(path: Path) -> str:
    """Return the SHA-256 checksum for a local file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_url_for_version(source_version_id: str) -> HttpUrl:
    versions = {version.id: version for version in load_source_versions()}
    return versions[source_version_id].source_url


def snapshot_local_file(
    *,
    source_id: str,
    source_version_id: str,
    path: Path,
    content_type: str,
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
) -> SourceSnapshotRecord:
    """Create a snapshot record for a local file."""
    root = project_root()
    resolved = path.resolve()
    local_path = str(resolved.relative_to(root)) if resolved.is_relative_to(root) else str(resolved)
    return SourceSnapshotRecord(
        id=f"snapshot_{source_version_id}",
        source_id=source_id,
        source_version_id=source_version_id,
        source_url=_source_url_for_version(source_version_id),
        local_path=local_path,
        retrieved_at="2026-07-03T00:00:00+10:00",
        content_type=content_type,
        byte_size=resolved.stat().st_size,
        checksum_sha256=file_sha256(resolved),
        licence_gate=licence_gate,
        cache_scope=cache_scope,
        notes="Synthetic no-network fixture snapshot for parser-contract testing.",
    )


def build_fixture_snapshots() -> list[SourceSnapshotRecord]:
    """Build snapshot records for committed synthetic parser fixtures."""
    root = project_root()
    return [
        snapshot_local_file(
            source_id=source_id,
            source_version_id=version_id,
            path=root / relative_path,
            content_type=content_type,
        )
        for version_id, (source_id, relative_path, content_type) in sorted(
            FIXTURE_SNAPSHOT_TARGETS.items()
        )
    ]


def write_snapshot_records(
    records: list[SourceSnapshotRecord],
    output_dir: Path,
) -> tuple[Path, Path]:
    """Write snapshot records as JSONL and CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "source_snapshots.jsonl"
    csv_path = output_dir / "source_snapshots.csv"
    rows = [record.model_dump(mode="json") for record in records]
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    fields = sorted({field for row in rows for field in row}) if rows else ["id"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return jsonl_path, csv_path

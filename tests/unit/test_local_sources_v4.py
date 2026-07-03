"""Tests for local-source validation commands and helpers."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.local_sources import (
    parse_reviewed_local_file,
    snapshot_reviewed_local_file,
    version_source_id,
)


def test_version_source_id_resolves_registered_seed_version() -> None:
    """Source version ids should map back to their registered source."""
    assert version_source_id("au_pbs_seed_fixture") == "au_pbs"


def test_snapshot_reviewed_local_file(repo_root: Path) -> None:
    """Reviewed local files should get checksum metadata without committing raw data."""
    record = snapshot_reviewed_local_file(
        source_version_id="au_pbs_seed_fixture",
        path=repo_root / "tests" / "fixtures" / "pbs_fixture.csv",
        content_type="text/csv",
        retrieved_at="2026-07-03T00:00:00+10:00",
        cache_scope="local_raw_only",
    )
    assert record.source_id == "au_pbs"
    assert record.cache_scope == "local_raw_only"
    assert record.checksum_sha256 is not None
    assert len(record.checksum_sha256) == 64


def test_parse_reviewed_local_file(repo_root: Path, tmp_path: Path) -> None:
    """Local parse helper should write derived rows for registered parser sources."""
    result = parse_reviewed_local_file(
        source_version_id="au_pbs_seed_fixture",
        path=repo_root / "tests" / "fixtures" / "pbs_fixture.csv",
        output_dir=tmp_path,
    )
    assert result.source_id == "au_pbs"
    assert result.record_type == "schedule_items"
    assert result.record_count == 2
    assert result.jsonl_path.exists()
    assert result.csv_path.exists()

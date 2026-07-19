"""Tests for local-source validation commands and helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import HttpUrl

from reimburse_atlas import local_sources
from reimburse_atlas.local_sources import (
    parse_reviewed_local_file,
    snapshot_reviewed_local_file,
    version_source_id,
)
from reimburse_atlas.models import SourceVersionRecord


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


def test_parse_reviewed_local_file_reports_unknown_mbs_version(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Unknown MBS versions should raise a useful error, not StopIteration."""
    version = SourceVersionRecord(
        id="au_mbs_missing",
        source_id="au_mbs",
        version_label="test",
        source_url=HttpUrl("https://example.com/mbs.xml"),
        format="xml",
        parser_status="validated",
        notes="test",
    )
    calls = 0

    def versions() -> list[SourceVersionRecord]:
        nonlocal calls
        calls += 1
        return [version] if calls == 1 else []

    monkeypatch.setattr(local_sources, "load_source_versions", versions)
    with pytest.raises(KeyError, match="Unknown source version id"):
        parse_reviewed_local_file(
            source_version_id=version.id,
            path=tmp_path / "missing.xml",
            output_dir=tmp_path / "output",
        )

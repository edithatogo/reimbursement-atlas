"""Tests for reviewed local source bundle workflow."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.local_sources import build_reviewed_source_bundle


def test_build_reviewed_source_bundle(repo_root: Path, tmp_path: Path) -> None:
    """A reviewed source bundle should include snapshot, parsed rows and reports."""
    result = build_reviewed_source_bundle(
        source_version_id="au_pbs_seed_fixture",
        path=repo_root / "tests" / "fixtures" / "pbs_fixture.csv",
        content_type="text/csv",
        output_dir=tmp_path,
        retrieved_at="2026-07-03T00:00:00+10:00",
    )
    assert result.source_id == "au_pbs"
    assert result.record_count == 2
    assert result.snapshot_jsonl_path.exists()
    assert result.parsed_jsonl_path.exists()
    assert result.validation_report_path.exists()
    assert result.publication_manifest_path.exists()
    assert "raw_file_copied" in result.publication_manifest_path.read_text(encoding="utf-8")

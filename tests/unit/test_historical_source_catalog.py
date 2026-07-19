"""Tests for the metadata-only multi-family historical source catalog."""

from __future__ import annotations

import json
from pathlib import Path


def test_historical_catalog_has_explicit_family_and_licence_gates(repo_root: Path) -> None:
    """Each discovered target is attributable to a family and reuse gate."""
    path = repo_root / "data/derived/historical_sources/historical_source_catalog.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) >= 50
    assert {
        "us_cms_pfs",
        "us_cms_asp",
        "us_cms_clfs",
        "uk_genomic_test_directory",
        "au_pbs",
    } <= {row["source_id"] for row in rows}
    assert all(row["licence_gate"] for row in rows)
    assert all(row["download_policy"] for row in rows)
    assert all(str(row["file_url"]).startswith("https://") for row in rows)

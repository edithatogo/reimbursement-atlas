"""Tests for parser prototypes."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.parsers import parse_schedule_item_fixture


def test_parse_schedule_item_fixture(repo_root: Path) -> None:
    """Fixture parser should emit normalised schedule item records."""
    path = repo_root / "tests" / "fixtures" / "schedule_items_fixture.jsonl"
    records = parse_schedule_item_fixture(path)
    assert len(records) == 2
    assert records[0].currency == "AUD"
    assert records[1].source_id == "us_cms_clfs"

"""Tests for current public-source status observations."""

from __future__ import annotations

from reimburse_atlas.registry import load_source_registry, load_source_status, source_ids


def test_source_status_records_resolve_to_registered_sources() -> None:
    """Every status observation should point at a registered source."""
    registered = source_ids(load_source_registry())
    records = load_source_status()
    assert len(records) >= 5
    assert {record.source_id for record in records} <= registered
    assert min(record.retrieval_priority for record in records) == 1

"""Tests for v5 seed-file synchronisation checks."""

from __future__ import annotations

from reimburse_atlas.validation import all_seed_pairs_ok, seed_pair_statuses


def test_seed_pair_statuses_are_ok_for_committed_seed_tables() -> None:
    """Core JSONL/CSV seed mirrors should be synchronised."""
    statuses = seed_pair_statuses()
    assert statuses
    assert all_seed_pairs_ok(statuses)
    assert {status.table_name for status in statuses} >= {
        "source_registry",
        "source_versions",
        "analysis_recipes",
        "ontology_concepts",
    }

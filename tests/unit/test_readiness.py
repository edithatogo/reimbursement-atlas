"""Tests for source and analysis readiness outputs."""

from __future__ import annotations

from reimburse_atlas.analysis import (
    analysis_readiness_rows,
    readiness_grade_sensitivity_rows,
    source_readiness_rows,
)
from reimburse_atlas.registry import load_analysis_catalogue, load_source_registry


def test_source_readiness_rows_include_scores() -> None:
    """Source readiness rows should be flat and dashboard-friendly."""
    rows = source_readiness_rows(load_source_registry())
    assert rows
    assert "component_machine_readable" in rows[0]
    assert max(int(row["score"]) for row in rows) >= 10


def test_analysis_readiness_rows_include_bottleneck() -> None:
    """Analysis readiness rows should surface source bottlenecks."""
    rows = analysis_readiness_rows(load_analysis_catalogue(), load_source_registry())
    assert rows
    assert "bottleneck_source_score" in rows[0]
    assert any(bool(row["ready_for_prototype"]) for row in rows)


def test_readiness_grade_sensitivity_preserves_source_count() -> None:
    """Alternative thresholds should partition, not change, the source set."""
    rows = readiness_grade_sensitivity_rows(
        load_source_registry(),
        [("canonical", 11, 8, 5), ("strict", 12, 9, 6)],
    )
    assert len(rows) == 2
    for row in rows:
        assert sum(int(row[f"grade_{grade}_count"]) for grade in "abcd") == row["source_count"]

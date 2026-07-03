"""Tests for source and analysis readiness outputs."""

from __future__ import annotations

from reimburse_atlas.analysis import analysis_readiness_rows, source_readiness_rows
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

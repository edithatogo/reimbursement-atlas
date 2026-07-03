"""Tests for transparent source-readiness scoring."""

from __future__ import annotations

from reimburse_atlas.registry import load_source_registry
from reimburse_atlas.scoring import grade_for_score, score_source, score_sources


def test_grade_thresholds() -> None:
    """Grade thresholds should be deterministic."""
    assert grade_for_score(12) == "A"
    assert grade_for_score(8) == "B"
    assert grade_for_score(5) == "C"
    assert grade_for_score(0) == "D"


def test_top_sources_have_nonzero_scores() -> None:
    """First-wave registries should score above zero."""
    scores = score_sources(load_source_registry())
    assert scores[0].score >= scores[-1].score
    assert score_source(load_source_registry()[0]).score > 0

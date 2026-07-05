"""Tests for deterministic string prefiltering."""

from __future__ import annotations

from reimburse_atlas.analysis.fuzzy_prefilter import fuzzy_prefilter


def test_fuzzy_prefilter_matches_identical_labels() -> None:
    left = ["genomic consultation", "pathology test"]
    right = ["genomic consultation", "radiology exam"]
    results = fuzzy_prefilter(left, right, threshold=0.3)
    assert results
    assert results[0][2] >= 0.9  # identical match


def test_fuzzy_prefilter_respects_threshold() -> None:
    left = ["completely unique service a"]
    right = ["completely unique service b"]
    results = fuzzy_prefilter(left, right, threshold=0.8)
    assert not results  # below threshold


def test_fuzzy_prefilter_max_per_left() -> None:
    left = ["test"]
    right = ["a", "b", "c", "d"]
    results = fuzzy_prefilter(left, right, threshold=0.0, max_per_left=2)
    assert len(results) <= 2

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.make_mapping_holdout_evaluation import build_evaluation, exact_interval


def test_exact_interval_matches_known_extreme_examples() -> None:
    assert exact_interval(0, 10)[1] == pytest.approx(0.308497, abs=1e-6)
    assert exact_interval(10, 10)[0] == pytest.approx(0.691503, abs=1e-6)


def test_evaluation_fails_closed_before_split(tmp_path: Path) -> None:
    result = build_evaluation(tmp_path)

    assert result["status"] == "blocked"
    assert result["exclusions"]["reason"] == "split_not_ready"
    assert result["evaluated_once"] is False

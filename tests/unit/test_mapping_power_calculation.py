from __future__ import annotations

import pytest

from scripts.make_mapping_power_calculation import (
    build_calculation,
    exact_one_sided_power_sample_size,
    one_sided_power_sample_size,
    proportion_precision_sample_size,
)


def test_confidence_interval_sample_size_matches_documented_formula() -> None:
    assert proportion_precision_sample_size(0.9, 0.05) == 139
    assert proportion_precision_sample_size(0.5, 0.05) == 385


def test_power_sample_size_matches_documented_scenario() -> None:
    assert one_sided_power_sample_size(0.8, 0.9) == 83


def test_exact_power_sample_size_reports_achieved_targets() -> None:
    result = exact_one_sided_power_sample_size(0.8, 0.9)
    assert result["cases_per_class"] == 82
    assert result["critical_positive_count"] == 72
    assert result["achieved_alpha"] <= 0.05
    assert result["achieved_power"] >= 0.8


def test_recommended_design_has_additional_holdout() -> None:
    result = build_calculation()["recommended_design"]
    assert result["development_cases_per_class"] == 300
    assert result["holdout_cases_per_class"] == 75
    assert result["total_cases_including_holdout"] == 750


@pytest.mark.parametrize(
    "args",
    [
        (0.0, 0.05),
        (1.0, 0.05),
        (0.9, 0.0),
    ],
)
def test_invalid_precision_inputs_fail_closed(args: tuple[float, float]) -> None:
    with pytest.raises(ValueError, match=r"must|between|exceed"):
        proportion_precision_sample_size(*args)

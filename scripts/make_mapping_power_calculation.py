"""Generate an auditable sample-size calculation for mapping calibration."""

# The report contains intentionally readable assumptions and formula descriptions.
# ruff: noqa: E501, EM101, TRY003

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import NormalDist
from typing import Any

from reimburse_atlas.registry import project_root, repo_relative

OUTPUT_JSON = project_root() / "data/derived/vertical_slice/mapping_power_calculation.json"
OUTPUT_MD = project_root() / "data/derived/vertical_slice/mapping_power_calculation.md"


def proportion_precision_sample_size(
    expected_proportion: float,
    half_width: float,
    confidence: float = 0.95,
) -> int:
    """Return the normal-approximation n for a two-sided proportion CI."""
    if not 0 < expected_proportion < 1:
        raise ValueError("expected_proportion must be between 0 and 1")
    if not 0 < half_width < 1:
        raise ValueError("half_width must be between 0 and 1")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    z = NormalDist().inv_cdf((1 + confidence) / 2)
    return math.ceil((z**2 * expected_proportion * (1 - expected_proportion)) / (half_width**2))


def one_sided_power_sample_size(
    null_proportion: float,
    alternative_proportion: float,
    alpha: float = 0.05,
    power: float = 0.8,
) -> int:
    """Return a normal-approximation n for a one-sample proportion test."""
    if not 0 < null_proportion < 1 or not 0 < alternative_proportion < 1:
        raise ValueError("proportions must be between 0 and 1")
    if alternative_proportion <= null_proportion:
        raise ValueError("alternative_proportion must exceed null_proportion")
    if not 0 < alpha < 1 or not 0 < power < 1:
        raise ValueError("alpha and power must be between 0 and 1")
    z_alpha = NormalDist().inv_cdf(1 - alpha)
    z_power = NormalDist().inv_cdf(power)
    numerator = z_alpha * math.sqrt(null_proportion * (1 - null_proportion)) + z_power * math.sqrt(
        alternative_proportion * (1 - alternative_proportion)
    )
    return math.ceil((numerator / (alternative_proportion - null_proportion)) ** 2)


def build_calculation() -> dict[str, Any]:
    """Build the deterministic calculation and document its assumptions."""
    ci_scenarios = [
        {"expected_metric": 0.90, "half_width": 0.05},
        {"expected_metric": 0.90, "half_width": 0.03},
        {"expected_metric": 0.80, "half_width": 0.05},
        {"expected_metric": 0.50, "half_width": 0.05},
    ]
    ci_rows = [
        {
            **scenario,
            "confidence": 0.95,
            "cases_per_class": proportion_precision_sample_size(
                scenario["expected_metric"], scenario["half_width"]
            ),
        }
        for scenario in ci_scenarios
    ]
    power_scenarios = [
        {"null_metric": 0.80, "alternative_metric": 0.90},
        {"null_metric": 0.90, "alternative_metric": 0.95},
    ]
    power_rows = [
        {
            **scenario,
            "alpha": 0.05,
            "power": 0.80,
            "cases_per_class": one_sided_power_sample_size(
                scenario["null_metric"], scenario["alternative_metric"]
            ),
        }
        for scenario in power_scenarios
    ]
    development_cases_per_class = 300
    holdout_fraction = 0.20
    holdout_cases_per_class = math.ceil(
        development_cases_per_class * holdout_fraction / (1 - holdout_fraction)
    )
    return {
        "schema_version": "mapping-power-calculation-v1",
        "method": "normal_approximation_for_binomial_proportions",
        "assumptions": [
            "Positive and negative calibration cases are sampled separately and treated as independent.",
            "Each case has one adjudicated reference outcome and one evaluated mapping outcome.",
            "The confidence-interval calculations use a two-sided 95% normal approximation.",
            "Power calculations use a one-sided alpha=0.05 test with 80% power.",
            "No clustering, spectrum bias, class imbalance, verification bias or missing adjudications is modelled.",
            "The synthetic four-case fixture is a smoke test and is not used to estimate the target metric.",
        ],
        "current_fixture": {
            "positive_cases": 2,
            "negative_cases": 2,
            "total_cases": 4,
            "evidence_use": "smoke_test_only",
        },
        "confidence_interval_scenarios": ci_rows,
        "power_scenarios": power_rows,
        "recommended_design": {
            "development_cases_per_class": development_cases_per_class,
            "development_total_cases": development_cases_per_class * 2,
            "independent_holdout_fraction": holdout_fraction,
            "holdout_cases_per_class": holdout_cases_per_class,
            "holdout_total_cases": holdout_cases_per_class * 2,
            "total_cases_including_holdout": (development_cases_per_class + holdout_cases_per_class)
            * 2,
            "rationale": "300 development cases per class gives approximately +/-3.4 points at an expected 90% metric and +/-4.5 points at an expected 80% metric; the holdout is additional.",
        },
        "limitations": [
            "The normal approximation is planning guidance, not an exact binomial power calculation.",
            "The design must be re-estimated if the estimand, acceptable null, prevalence, clustering or adjudication protocol changes.",
            "Cases must be stratified across sources and mapping difficulty; duplicating near-identical cases does not increase effective sample size.",
        ],
        "generated_from": repo_relative(Path(__file__), project_root()),
    }


def render_markdown(result: dict[str, Any]) -> str:
    """Render assumptions, formulas and outcomes for human review."""
    design = result["recommended_design"]
    lines = [
        "# Mapping Calibration Power Calculation",
        "",
        "This generated report replaces an informal sample-size estimate. It uses",
        "explicit normal-approximation formulas and is planning guidance, not evidence",
        "of mapping performance.",
        "",
        "## Current fixture",
        "",
        "The current fixture has **4 cases**: 2 positive cases and 2 negative controls.",
        "It remains a smoke test only.",
        "",
        "## Assumptions",
        "",
    ]
    lines.extend(f"- {assumption}" for assumption in result["assumptions"])
    lines.extend([
        "",
        "## Calculation",
        "",
        "For confidence-interval planning, the implementation uses `n = z^2 p(1-p) / d^2`.",
        "For one-sided power planning, it uses the standard normal approximation combining",
        "the null and alternative variances. Both formulas are implemented in",
        "`scripts/make_mapping_power_calculation.py` and covered by unit tests.",
        "",
        "| Expected metric | CI half-width | Cases per class |",
        "| ---: | ---: | ---: |",
    ])
    lines.extend(
        f"| {row['expected_metric']:.0%} | +/-{row['half_width']:.0%} | {row['cases_per_class']} |"
        for row in result["confidence_interval_scenarios"]
    )
    lines.extend([
        "",
        "| Null metric | Alternative metric | Alpha | Power | Cases per class |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ])
    lines.extend(
        f"| {row['null_metric']:.0%} | {row['alternative_metric']:.0%} | {row['alpha']:.0%} | {row['power']:.0%} | {row['cases_per_class']} |"
        for row in result["power_scenarios"]
    )
    lines.extend([
        "",
        "## Recommended design",
        "",
        f"- Development set: **{design['development_cases_per_class']} positive + {design['development_cases_per_class']} negative = {design['development_total_cases']} cases**.",
        f"- Independent holdout: **{design['holdout_cases_per_class']} positive + {design['holdout_cases_per_class']} negative = {design['holdout_total_cases']} cases**.",
        f"- Total including holdout: **{design['total_cases_including_holdout']} cases**.",
        f"- Rationale: {design['rationale']}",
        "",
        "Cases should be stratified across MBS, PBS, CMS, genomics, procedures, medicines,",
        "devices and ambiguous mappings. Near-duplicate cases do not provide independent",
        "information.",
        "",
        "## Limitations",
        "",
    ])
    lines.extend(f"- {limitation}" for limitation in result["limitations"])
    return "\n".join(lines) + "\n"


def main() -> None:
    """Write the machine-readable and reviewer-facing reports."""
    result = build_calculation()
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(result), encoding="utf-8")
    print(
        f"Wrote mapping power calculation: {repo_relative(OUTPUT_JSON)}, {repo_relative(OUTPUT_MD)}"
    )


if __name__ == "__main__":
    main()

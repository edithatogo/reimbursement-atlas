"""Tests for policy signal matrix prototypes."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.analysis.policy_matrix import policy_signal_matrix
from reimburse_atlas.parsers import parse_mbs_xml, parse_nhs_genomic_directory_csv


def test_policy_signal_matrix_separates_price_and_coverage_sources(repo_root: Path) -> None:
    """Policy signal rows should support separate price and coverage sources."""
    schedule = parse_mbs_xml(repo_root / "tests" / "fixtures" / "mbs_fragment.xml")
    coverage = parse_nhs_genomic_directory_csv(
        repo_root / "tests" / "fixtures" / "nhs_genomic_directory_fixture.csv"
    )
    rows = policy_signal_matrix(schedule, coverage)
    by_source = {str(row["source_id"]): row for row in rows}
    assert by_source["au_mbs"]["policy_use"] == "price_schedule_comparison"
    assert by_source["uk_genomic_test_directory"]["policy_use"] == (
        "coverage_architecture_comparison"
    )

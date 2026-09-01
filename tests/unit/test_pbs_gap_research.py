"""Regression tests for bounded residual PBS archive-gap evidence."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.make_pbs_gap_research import build_summary, main


def test_gap_evidence_keeps_catalogue_and_payload_claims_distinct() -> None:
    summary = build_summary()
    rpbs = summary["rpbs_1987"]
    assert isinstance(rpbs, dict)
    assert rpbs["catalogue_record_inspected"] is True
    assert rpbs["target_issue_inspected"] is False
    assert rpbs["digitised_copy_acquired"] is False
    assert rpbs["access_mode"] == "request_for_main_reading_room_use"


def test_gap_evidence_does_not_promote_publication_views_to_structured_data() -> None:
    summary = build_summary()
    releases = summary["monthly_structured_releases"]
    assert isinstance(releases, dict)
    assert releases["observed_endpoint_kind"] == "flashpaper_publication_view"
    assert releases["monthly_releases_recovered"] == 0
    assert releases["monthly_schema_assignment_verified"] is False
    assert releases["structured_api_equivalence"] is False


def test_gap_evidence_generation_is_deterministic(tmp_path: Path) -> None:
    output = tmp_path / "summary.json"
    main(output)
    first = output.read_bytes()
    main(output)
    assert output.read_bytes() == first
    assert json.loads(first)["claim_boundaries"]["raw_content_in_git"] is False


def test_committed_gap_evidence_matches_generator() -> None:
    path = Path("data/derived/historical_sources/pbs_gap_research_v1/summary.json")
    assert json.loads(path.read_text(encoding="utf-8")) == build_summary()

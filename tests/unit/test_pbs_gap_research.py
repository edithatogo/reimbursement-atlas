"""Regression tests for bounded residual PBS archive-gap evidence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.make_pbs_gap_research import build_query_receipts, build_summary, main


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


def test_archive_search_aggregates_are_derived_from_path_free_receipts() -> None:
    receipts = build_query_receipts()
    structured = [row for row in receipts if row["query_class"] == "structured_payload"]
    summary = build_summary(receipts)["monthly_structured_releases"]
    assert isinstance(summary, dict)
    assert summary["structured_payload_prefix_queries"] == len(structured) == 3
    assert summary["structured_payload_prefix_matches"] == 0
    assert summary["structured_payload_query_response_sha256"] == [
        "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"
    ]
    assert all(str(row["query_url"]).startswith("https://web.archive.org/cdx/") for row in receipts)
    assert all("raw_live" not in json.dumps(row) for row in receipts)


def test_duplicate_archive_query_receipts_fail_closed() -> None:
    receipts = build_query_receipts()
    with pytest.raises(ValueError, match="duplicate archive query receipt id"):
        build_summary([*receipts, receipts[0]])


def test_gap_evidence_generation_is_deterministic(tmp_path: Path) -> None:
    output = tmp_path / "summary.json"
    main(output)
    first = output.read_bytes()
    main(output)
    assert output.read_bytes() == first
    assert json.loads(first)["claim_boundaries"]["raw_content_in_git"] is False
    receipts = output.with_name("archive_query_receipts.jsonl")
    assert len(receipts.read_text(encoding="utf-8").splitlines()) == 4


def test_committed_gap_evidence_matches_generator() -> None:
    path = Path("data/derived/historical_sources/pbs_gap_research_v1/summary.json")
    assert json.loads(path.read_text(encoding="utf-8")) == build_summary()
    receipts = path.with_name("archive_query_receipts.jsonl")
    assert [json.loads(line) for line in receipts.read_text(encoding="utf-8").splitlines()] == (
        build_query_receipts()
    )

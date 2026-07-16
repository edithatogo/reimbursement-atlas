"""Tests for the first-wave source URL and licence checklist."""

from pathlib import Path

from scripts.make_source_url_licence_checklist import build_checklist


def test_checklist_covers_first_wave_source_files() -> None:
    rows = build_checklist(Path(__file__).parents[2])
    assert rows
    assert {row["source_id"] for row in rows} >= {
        "au_mbs",
        "au_pbs",
        "us_cms_asp",
        "us_cms_clfs",
        "us_cms_pfs",
    }
    assert all(row["url_verification_status"] == "pending_human_verification" for row in rows)
    assert all(row["licence_review_status"] == "pending_human_review" for row in rows)
    assert all(row["raw_handling"] == "ignored_local_only" for row in rows)

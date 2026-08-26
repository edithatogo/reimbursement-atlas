"""Regression tests for evidence-backed Conductor backlog states."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _backlog_issues() -> dict[str, dict[str, object]]:
    payload = yaml.safe_load((ROOT / "conductor/backlog.yml").read_text(encoding="utf-8"))
    return {
        str(issue["title"]): issue for epic in payload["epics"] for issue in epic.get("issues", [])
    }


def _validation_report(bundle: str) -> dict[str, object]:
    path = ROOT / "data/derived/reviewed_source_bundles" / bundle / "validation_report.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_completed_live_parser_reviews_have_real_bundle_evidence() -> None:
    issues = _backlog_issues()
    evidence = {
        "Review first real July 2026 MBS TXT pair bundle outputs": (
            "bundle_au_mbs_20260701_txt_pair_f3c1caae1fe830ae",
            None,
        ),
        "Validate CMS CLFS parser against one public file without CPT descriptor redistribution": (
            "snapshot_us_cms_clfs_26clabq3_ama_zip_f5a090789c40",
            2206,
        ),
        "Validate PBS API CSV parser against a reviewed monthly public extract": (
            "bundle_au_pbs_api_v3_current_month_648b7b12ceb319f1",
            6945,
        ),
        "Validate CMS ASP parser against July 2026 payment-limit files": (
            "snapshot_us_cms_asp_july_2026_payment_limit_c73883dbddb5",
            890,
        ),
        "Validate CMS PFS parser against RVU26C with CPT descriptor safeguards": (
            "snapshot_us_cms_pfs_2026_revision_c_carrier_1ba04e577235",
            1635,
        ),
    }

    for title, (bundle, expected_records) in evidence.items():
        assert issues[title]["status"] == "implemented"
        report = _validation_report(bundle)
        assert report.get("parse_success", True) is True
        assert report.get("raw_file_copied_to_bundle", False) is False
        if expected_records is not None:
            assert report["record_count"] == expected_records


def test_hosted_pbs_refresh_clears_stale_credential_gate() -> None:
    metadata = json.loads(
        (ROOT / "conductor/archive/track_live_source_ingestion/metadata.json").read_text(
            encoding="utf-8"
        )
    )
    gate = next(item for item in metadata["gates"] if item["id"] == "pbs_api_credential")
    assert gate["status"] == "pass"
    assert "32951770117" in gate["evidence"]
    assert "14,867" in gate["evidence"]


def test_completed_tracks_are_archived_consistently() -> None:
    registry = yaml.safe_load((ROOT / "conductor/tracks.yml").read_text(encoding="utf-8"))
    tracks = {item["id"]: item for item in registry["tracks"]}

    for track_id in (
        "track_live_source_ingestion",
        "track_continuous_security_assurance",
    ):
        track = tracks[track_id]
        metadata = json.loads(
            ROOT.joinpath("conductor/archive", track_id, "metadata.json").read_text(
                encoding="utf-8"
            )
        )
        assert track["phase"] == "archived"
        assert metadata["status"] == "completed"
        assert track["spec"].startswith("conductor/archive/")
        assert track["plan"].startswith("conductor/archive/")


def test_bounded_analyses_are_complete_without_claiming_papers() -> None:
    issues = _backlog_issues()
    item = issues[
        "Run five protocolled analyses on reviewed derived inputs and review claim packages"
    ]
    summary = json.loads(
        (ROOT / "data/derived/research_claims/summary.json").read_text(encoding="utf-8")
    )

    assert summary["complete_count"] == 5
    assert summary["approved_within_scope_count"] == 5
    assert summary["pending_accountable_review_count"] == 0
    assert item["status"] == "implemented"
    assert "bounded evidence reports are complete" in item["acceptance"][1]
    assert "preprints remain intentionally excluded" in item["acceptance"][1]


def test_external_monitoring_items_preserve_true_platform_state() -> None:
    issues = _backlog_issues()
    assert (
        issues["Enable GitHub non-provider secret-pattern scanning and validity checks"]["status"]
        == "implemented"
    )
    assert (
        issues["Reassess TypeScript 7 after Astro checker peer support is available"]["status"]
        == "monitored"
    )


def test_monitored_external_dependency_has_completed_monitoring_contract() -> None:
    draft = (
        ROOT
        / ".github/generated-issues"
        / "175-reassess-typescript-7-after-astro-checker-peer-support-is-available.md"
    ).read_text(encoding="utf-8")

    assert "Status: `monitored`" in draft
    assert "- [ ]" not in draft
    assert "never a repository release blocker" in draft

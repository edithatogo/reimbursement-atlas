"""Contracts for the public product and dashboard status surface."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.check_public_docs import build_public_docs_report, current_state_commits
from scripts.make_public_status_manifest import build_public_status_manifest
from scripts.sync_dashboard_seed import sanitise_public_text
from scripts.validate_citation import validate_citation


def test_citation_metadata_passes_repository_contract() -> None:
    """The tracked citation file contains the required public software metadata."""
    errors = validate_citation(Path("CITATION.cff"))
    assert errors == []


def test_public_status_separates_software_evidence_and_publication(tmp_path: Path) -> None:
    """The status manifest remains fail-closed when evidence summaries are incomplete."""
    for relative, payload in {
        "data/derived/release_readiness/summary.json": {
            "repository_release_ready": True,
            "evidence_release_ready": False,
            "research_publication_ready": False,
            "osf_registration_ready": False,
        },
        "data/derived/evidence_readiness/summary.json": {"row_count": 2},
        "data/derived/data_quality/summary.json": {"status": "warn"},
        "data/derived/source_validation/summary.json": {"status": "blocked"},
    }.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    handoff_path = tmp_path / "data/derived/final_handoff/final_handoff_tasks.jsonl"
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_path.write_text(
        json.dumps({
            "id": "final_source_downloads",
            "status": "partial",
            "task_group": "source_ingestion",
            "title": "Run hardened source download plan",
        })
        + "\n",
        encoding="utf-8",
    )
    source_health_path = tmp_path / "data/derived/source_health/acquisition_status.json"
    source_health_path.parent.mkdir(parents=True, exist_ok=True)
    source_health_path.write_text(
        json.dumps({"status": "incomplete", "incomplete_count": 1}),
        encoding="utf-8",
    )

    manifest = build_public_status_manifest(tmp_path)

    assert manifest["software"]["status"] == "ready"
    assert manifest["evidence"]["status"] == "not_ready"
    assert manifest["publication"]["status"] == "gated"
    assert manifest["evidence"]["source_validation"] == "blocked"
    assert manifest["evidence_paths"]["source_health"] == (
        "data/derived/source_health/acquisition_status.json"
    )
    assert {item["id"] for item in manifest["blockers"]} >= {
        "evidence_release",
        "research_publication",
        "osf_registration",
        "source_acquisition",
    }


def test_public_status_does_not_duplicate_licence_only_source_review(tmp_path: Path) -> None:
    """Review-only acquisition rows remain governed by the licence blocker."""
    for relative, payload in {
        "data/derived/release_readiness/summary.json": {
            "repository_release_ready": True,
            "evidence_release_ready": False,
            "research_publication_ready": False,
            "osf_registration_ready": False,
        },
        "data/derived/evidence_readiness/summary.json": {"row_count": 1},
        "data/derived/data_quality/summary.json": {"blocking_failures": 0},
        "data/derived/source_validation/summary.json": {"blocking_failures": 0},
        "data/derived/licence_review/summary.json": {"pending_count": 1},
        "data/derived/source_health/acquisition_status.json": {
            "status": "review_required",
            "incomplete_count": 1,
            "operational_blocker_count": 0,
            "review_required_count": 6,
        },
    }.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    handoff_path = tmp_path / "data/derived/final_handoff/final_handoff_tasks.jsonl"
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_path.write_text(
        json.dumps({
            "id": "final_source_downloads",
            "status": "partial",
            "task_group": "source_ingestion",
            "title": "Run hardened source download plan",
        })
        + "\n",
        encoding="utf-8",
    )

    manifest = build_public_status_manifest(tmp_path)
    assert "source_acquisition" not in {item["id"] for item in manifest["blockers"]}
    assert "licence_review" in {item["id"] for item in manifest["blockers"]}


def test_public_dashboard_assets_redact_local_raw_cache_paths() -> None:
    """Public derived assets must not expose ignored local raw-cache locations."""
    result = sanitise_public_text("source=data/raw_live/mbs/file.txt")

    assert "data/raw_live" not in result
    assert "[ignored-local-raw-cache]/mbs/file.txt" in result


def test_public_docs_report_is_machine_readable() -> None:
    """Documentation freshness emits a passing report for the repository contract."""
    report = build_public_docs_report(Path())

    assert report["schema_version"] == "public-docs-v1"
    assert report["status"] == "pass"
    assert report["error_count"] == 0


def test_public_docs_verify_code_and_data_licence_boundary() -> None:
    """Public documentation must preserve Apache code and source-data boundaries."""
    report = build_public_docs_report(Path())

    assert "LICENSE" in report["checked_files"]
    assert "NOTICE" in report["checked_files"]


def test_current_state_commits_support_pr_and_post_merge_checkouts(monkeypatch) -> None:
    """The freshness gate accepts a PR base and its eventual first-parent merge."""
    values = {
        "origin/main": "a" * 40,
        "HEAD^1": "a" * 40,
        "HEAD": "b" * 40,
    }
    monkeypatch.setattr(
        "scripts.check_public_docs.git_commit",
        lambda _root, revision: values.get(revision),
    )

    assert current_state_commits(Path()) == ("a" * 40, "b" * 40)

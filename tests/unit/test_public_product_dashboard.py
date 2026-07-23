"""Contracts for the public product and dashboard status surface."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.check_public_docs import (
    build_public_docs_report,
    current_state_commits,
    git_is_ancestor,
)
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
    release_gates_path = tmp_path / "data/derived/release_readiness/release_gates.jsonl"
    release_gates_path.write_text(
        "\n".join([
            json.dumps({
                "id": "mapping_study_human_review",
                "category": "data_governance",
                "status": "blocked",
                "evidence": "mapping review incomplete",
                "recommended_action": "Complete adjudication.",
            }),
            json.dumps({
                "id": "dashboard_human_review",
                "category": "dashboard",
                "status": "blocked",
                "evidence": "dashboard review incomplete",
                "recommended_action": "Complete scoped review.",
            }),
        ])
        + "\n",
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
        "mapping_study_human_review",
        "dashboard_human_review",
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


def test_public_status_uses_current_checksum_bound_decisions(tmp_path: Path) -> None:
    """The status projection counts valid ledger decisions, not neutral queue rows."""
    for relative, payload in {
        "data/derived/release_readiness/summary.json": {
            "repository_release_ready": True,
            "evidence_release_ready": False,
            "research_publication_ready": False,
            "osf_registration_ready": False,
        },
        "data/derived/evidence_readiness/summary.json": {},
        "data/derived/data_quality/summary.json": {"blocking_failures": 0},
        "data/derived/source_validation/summary.json": {"blocking_failures": 0},
    }.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    queue_path = tmp_path / "data/derived/licence_review/licence_review_queue.jsonl"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_rows = [
        {"review_id": "one", "relative_path": "README.md", "checksum_sha256": "a" * 64},
        {"review_id": "two", "relative_path": "README.md", "checksum_sha256": "b" * 64},
    ]
    queue_path.write_text("\n".join(json.dumps(row) for row in queue_rows) + "\n")
    decisions_path = tmp_path / "data/licence_review/decisions.jsonl"
    decisions_path.parent.mkdir(parents=True, exist_ok=True)
    decisions_path.write_text(
        json.dumps({
            "review_id": "one",
            "relative_path": "README.md",
            "checksum_sha256": "a" * 64,
            "decision": "approved",
        })
        + "\n"
    )
    (tmp_path / "README.md").write_text("fixture\n")

    manifest = build_public_status_manifest(tmp_path)

    assert manifest["licence_review"] == {
        "approved_rows": 1,
        "pending_rows": 1,
        "decision_source": "data/licence_review/decisions.jsonl",
        "queue_source": "data/derived/licence_review/licence_review_queue.jsonl",
    }
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


def test_git_is_ancestor_uses_a_shell_free_fixed_argv(monkeypatch) -> None:
    """Snapshot validation can accept an older commit without accepting arbitrary text."""
    calls = []

    class Result:
        returncode = 0

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs))
        return Result()

    monkeypatch.setattr("scripts.check_public_docs.subprocess.run", fake_run)

    assert git_is_ancestor(Path(), "a" * 40)
    assert calls[0][0] == ["git", "merge-base", "--is-ancestor", "a" * 40, "HEAD"]
    assert calls[0][1].get("shell") is not True


def test_tracked_public_status_counts_match_decision_ledger(repo_root: Path) -> None:
    """Prevent a merged handoff from publishing stale licence counts."""
    status = json.loads(
        (repo_root / "apps/dashboard/public/status.json").read_text(encoding="utf-8")
    )
    decisions = [
        json.loads(line)
        for line in (repo_root / "data/licence_review/decisions.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    approved = sum(row.get("decision") == "approved" for row in decisions)
    blocked = sum(row.get("decision") == "blocked" for row in decisions)
    assert status["licence_review"]["approved_rows"] == approved
    assert status["licence_review"]["pending_rows"] == blocked

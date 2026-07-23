from __future__ import annotations

import json
from pathlib import Path

import pytest

from reimburse_atlas.dashboard_review import (
    dashboard_data_fingerprint,
    dashboard_review_evidence,
    dashboard_source_fingerprint,
    resolve_repo_head,
)
from scripts.make_dashboard_owner_review_packet import PROVENANCE_INPUTS, build_packet
from scripts.make_dashboard_review_packet import PROJECTS, ROUTES
from scripts.make_public_status_manifest import build_public_status_manifest


def _write_json(root: Path, relative: str, value: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _machine_ready_root(tmp_path: Path) -> Path:
    commit = "a" * 40
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git/HEAD").write_text(commit, encoding="utf-8")
    _write_json(
        tmp_path,
        "data/derived/dashboard_review/automated_review_packet.json",
        {
            "status": "pass",
            "tested_commit": commit,
            "coverage_complete": True,
            "routes": list(ROUTES),
            "projects": list(PROJECTS),
            "test_count": 64,
            "screenshots": [
                {"route": route, "project": project} for route in ROUTES for project in PROJECTS
            ],
            "workflow": {
                "workflow": "Dashboard browser matrix",
                "run_id": "123",
                "run_attempt": "1",
                "artifact_name": "dashboard-browser-review-123",
                "workflow_url": "https://github.com/owner/repo/actions/runs/123",
            },
        },
    )
    _write_json(
        tmp_path,
        "data/derived/source_validation/summary.json",
        {"status": "pass", "blocking_failures": 0},
    )
    _write_json(tmp_path, "data/derived/evidence_readiness/summary.json", {})
    _write_json(
        tmp_path,
        "data/derived/release_readiness/summary.json",
        {
            "evidence_release_ready": False,
            "repository_release_ready": True,
            "research_publication_ready": False,
            "osf_registration_ready": False,
        },
    )
    _write_json(tmp_path, "data/derived/publication_manifest.json", {"status": "gated"})
    _write_json(
        tmp_path,
        "apps/dashboard/public/status.json",
        build_public_status_manifest(tmp_path),
    )
    automated_path = tmp_path / "data/derived/dashboard_review/automated_review_packet.json"
    automated = json.loads(automated_path.read_text(encoding="utf-8"))
    automated["source_fingerprint"] = dashboard_source_fingerprint(tmp_path)
    automated["data_fingerprint"] = dashboard_data_fingerprint(tmp_path)
    automated_path.write_text(json.dumps(automated), encoding="utf-8")
    return tmp_path


def test_owner_packet_is_machine_ready_but_does_not_imply_human_approval(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    packet = build_packet(_machine_ready_root(tmp_path))

    assert packet["status"] == "pending_accountable_review"
    assert packet["commit_parity"] is True
    assert packet["route_coverage_bounded"] is True
    assert packet["screenshot_count"] == 44
    assert all(row["status"] == "pass" for row in packet["provenance_assertions"])
    assert packet["prohibited_content_check"]["status"] == "pass"
    assert "approved_within_scope" in packet["accountable_checklist"][-1]


def test_owner_packet_blocks_prohibited_public_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    root = _machine_ready_root(tmp_path)
    (root / "apps/dashboard/public/leak.txt").write_text(
        "source=/Users/example/data/raw_live/payload.csv",
        encoding="utf-8",
    )

    packet = build_packet(root)

    assert packet["status"] == "automated_evidence_blocked"
    check = packet["prohibited_content_check"]
    assert check["status"] == "fail"
    assert {row["rule"] for row in check["findings"]} == {
        "local_absolute_path",
        "raw_live_path",
    }


def test_current_owner_packet_is_ready_for_bounded_accountable_review() -> None:
    packet = build_packet(Path.cwd())

    assert packet["status"] in {"pending_accountable_review", "automated_evidence_blocked"}
    assert packet["routes"] == list(ROUTES)
    assert packet["screenshot_count"] == 44
    assert packet["automated_test_count"] == 64
    assert len(packet["provenance_inputs"]) >= 4


def test_dashboard_evidence_serializes_stable_evidence_commit(tmp_path: Path) -> None:
    automated = tmp_path / "data/derived/dashboard_review/automated_review_packet.json"
    automated.parent.mkdir(parents=True)
    automated.write_text(
        json.dumps({
            "tested_commit": "a" * 40,
            "source_fingerprint": dashboard_source_fingerprint(tmp_path),
            "data_fingerprint": dashboard_data_fingerprint(tmp_path),
        }),
        encoding="utf-8",
    )
    git = tmp_path / ".git"
    git.mkdir()
    (git / "HEAD").write_text("b" * 40, encoding="utf-8")

    evidence = dashboard_review_evidence(tmp_path)

    assert evidence["head"] == "a" * 40
    assert evidence["checks"]["head_parity"] is False


def test_dashboard_evidence_invalidates_changed_displayed_data(tmp_path: Path) -> None:
    root = _machine_ready_root(tmp_path)
    owner = build_packet(root)
    owner_path = root / "data/derived/dashboard_review/owner_review_packet.json"
    owner_path.parent.mkdir(parents=True, exist_ok=True)
    owner_path.write_text(json.dumps(owner), encoding="utf-8")
    status_path = root / "apps/dashboard/public/status.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status["publication"]["osf_registration_ready"] = True
    status_path.write_text(json.dumps(status), encoding="utf-8")

    evidence = dashboard_review_evidence(root)

    assert evidence["checks"]["displayed_data_parity"] is False


def test_owner_packet_does_not_hash_its_dependent_release_summary() -> None:
    """Prevent a cryptographic cycle between review evidence and release readiness."""
    assert Path("data/derived/release_readiness/summary.json") not in PROVENANCE_INPUTS


def test_resolve_repo_head_reads_detached_and_loose_refs(tmp_path: Path) -> None:
    git = tmp_path / ".git"
    git.mkdir()
    (git / "HEAD").write_text("a" * 40, encoding="utf-8")
    assert resolve_repo_head(tmp_path) == "a" * 40

    (git / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
    branch = git / "refs/heads/main"
    branch.parent.mkdir(parents=True)
    branch.write_text("b" * 40, encoding="utf-8")
    assert resolve_repo_head(tmp_path) == "b" * 40


def test_resolve_repo_head_reads_worktree_packed_ref(tmp_path: Path) -> None:
    common = tmp_path / "common"
    worktree_git = common / "worktrees/current"
    worktree_git.mkdir(parents=True)
    (worktree_git / "HEAD").write_text("ref: refs/heads/release", encoding="utf-8")
    (worktree_git / "commondir").write_text("../..", encoding="utf-8")
    (common / "packed-refs").write_text(
        f"# pack-refs\n{'c' * 40} refs/heads/release\n^{'d' * 40}\n",
        encoding="utf-8",
    )
    (tmp_path / ".git").write_text(
        f"gitdir: {worktree_git.as_posix()}",
        encoding="utf-8",
    )

    assert resolve_repo_head(tmp_path) == "c" * 40


def test_resolve_repo_head_rejects_invalid_gitdir_marker(tmp_path: Path) -> None:
    (tmp_path / ".git").write_text("invalid", encoding="utf-8")

    assert resolve_repo_head(tmp_path) is None

from __future__ import annotations

import json
from pathlib import Path

import pytest

from reimburse_atlas.dashboard_review import dashboard_review_evidence
from scripts.make_dashboard_owner_review_packet import build_packet
from scripts.make_dashboard_review_packet import PROJECTS, ROUTES


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
        "apps/dashboard/public/status.json",
        {
            "evidence": {
                "source_validation": "pass",
                "evidence_release_ready": False,
                "research_publication_ready": False,
            },
            "software": {"repository_release_ready": True},
        },
    )
    _write_json(tmp_path, "data/derived/source_validation/summary.json", {"status": "pass"})
    _write_json(
        tmp_path,
        "data/derived/evidence_readiness/summary.json",
        {"evidence_release_ready": False},
    )
    _write_json(
        tmp_path,
        "data/derived/release_readiness/summary.json",
        {"repository_release_ready": True, "research_publication_ready": False},
    )
    _write_json(tmp_path, "data/derived/publication_manifest.json", {"status": "gated"})
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


def test_owner_packet_fails_closed_for_stale_legacy_evidence() -> None:
    packet = build_packet(Path.cwd())

    assert packet["status"] == "automated_evidence_blocked"
    assert packet["routes"] == []
    assert packet["screenshot_count"] == 0
    assert packet["automated_test_count"] == 64
    assert len(packet["provenance_inputs"]) >= 4


def test_dashboard_evidence_serializes_stable_evidence_commit(tmp_path: Path) -> None:
    automated = tmp_path / "data/derived/dashboard_review/automated_review_packet.json"
    automated.parent.mkdir(parents=True)
    automated.write_text(
        json.dumps({"tested_commit": "a" * 40}),
        encoding="utf-8",
    )
    git = tmp_path / ".git"
    git.mkdir()
    (git / "HEAD").write_text("b" * 40, encoding="utf-8")

    evidence = dashboard_review_evidence(tmp_path)

    assert evidence["head"] == "a" * 40
    assert evidence["checks"]["head_parity"] is False

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.make_dashboard_review_packet import build_packet, resolve_head


def test_dashboard_packet_hashes_expected_screenshot_matrix(tmp_path: Path) -> None:
    report = tmp_path / "report/data"
    report.mkdir(parents=True)
    for index in range(36):
        (report / f"{index:02}.png").write_bytes(b"png" + bytes([index]))

    packet = build_packet(tmp_path / "report", "a" * 40)
    schema = json.loads(
        Path("schema/DashboardAutomatedReviewPacket.schema.json").read_text(encoding="utf-8")
    )

    assert packet["status"] == "pass"
    assert packet["screenshot_count"] == 36
    assert packet["human_review_required"] is True
    assert not list(Draft202012Validator(schema).iter_errors(packet))


def test_dashboard_packet_fails_closed_when_artifacts_are_missing(tmp_path: Path) -> None:
    packet = build_packet(tmp_path / "missing", "b" * 40)

    assert packet["status"] == "missing_artifacts"
    assert packet["screenshot_count"] == 0
    assert packet["human_review_required"] is True


def test_head_resolves_loose_and_packed_git_refs(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (git_dir / "packed-refs").write_text(f"{'a' * 40} refs/heads/main\n", encoding="utf-8")
    assert resolve_head(tmp_path) == "a" * 40

    loose = git_dir / "refs/heads/main"
    loose.parent.mkdir(parents=True)
    loose.write_text("b" * 40 + "\n", encoding="utf-8")
    assert resolve_head(tmp_path) == "b" * 40


def test_head_prefers_ci_commit(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("GITHUB_SHA", "c" * 40)
    assert resolve_head(tmp_path) == "c" * 40


def test_head_resolves_ref_from_worktree_common_git_dir(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    common = tmp_path / "common"
    worktree_git = common / "worktrees" / "review"
    worktree_git.mkdir(parents=True)
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").write_text(
        f"gitdir: {worktree_git.relative_to(project, walk_up=True)}\n",
        encoding="utf-8",
    )
    (worktree_git / "HEAD").write_text("ref: refs/heads/review\n", encoding="utf-8")
    (worktree_git / "commondir").write_text("../..\n", encoding="utf-8")
    (common / "packed-refs").write_text(
        f"{'d' * 40} refs/heads/review\n",
        encoding="utf-8",
    )

    assert resolve_head(project) == "d" * 40

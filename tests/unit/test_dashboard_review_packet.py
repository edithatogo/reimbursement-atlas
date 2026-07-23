from __future__ import annotations

import base64
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from scripts.make_dashboard_review_packet import (
    EXPECTED_TEST_COUNT,
    PROJECTS,
    ROUTES,
    build_packet,
    resolve_head,
)


def _write_reports(report: Path, *, failed: bool = False, omit_pair: bool = False) -> None:
    report.mkdir(parents=True)
    tests: list[dict[str, object]] = []
    for project in PROJECTS:
        for route in ROUTES:
            if omit_pair and project == PROJECTS[-1] and route == ROUTES[-1]:
                continue
            context = {
                "route": route,
                "project": project,
                "viewport": {"width": 1280, "height": 720},
                "browser": (
                    "firefox"
                    if "firefox" in project
                    else "webkit"
                    if "webkit" in project
                    else "chromium"
                ),
                "browserVersion": "123.0",
            }
            tests.append({
                "projectName": project,
                "results": [
                    {
                        "status": "failed" if failed and not tests else "passed",
                        "attachments": [
                            {
                                "name": "route-screenshot",
                                "contentType": "image/png",
                                "body": base64.b64encode(
                                    f"png:{project}:{route}".encode()
                                ).decode(),
                            },
                            {
                                "name": "dashboard-review-context",
                                "contentType": "application/json",
                                "body": base64.b64encode(json.dumps(context).encode()).decode(),
                            },
                        ],
                    }
                ],
            })
    while len(tests) < EXPECTED_TEST_COUNT:
        tests.append({
            "projectName": PROJECTS[len(tests) % len(PROJECTS)],
            "results": [{"status": "passed", "attachments": []}],
        })
    report.joinpath("results.json").write_text(
        json.dumps({"suites": [{"specs": [{"tests": tests}]}]}),
        encoding="utf-8",
    )
    failures = 1 if failed else 0
    report.joinpath("results.xml").write_text(
        (
            f'<testsuites><testsuite tests="{len(tests)}" failures="{failures}" '
            'errors="0" skipped="0"/></testsuites>'
        ),
        encoding="utf-8",
    )


def test_dashboard_packet_parses_attributable_complete_matrix(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    report = tmp_path / "report"
    _write_reports(report)
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    monkeypatch.setenv("GITHUB_WORKFLOW", "Dashboard browser matrix")

    packet = build_packet(
        report,
        "a" * 40,
        source_fingerprint="b" * 64,
        data_fingerprint="c" * 64,
    )
    schema = json.loads(
        Path("schema/DashboardAutomatedReviewPacket.schema.json").read_text(encoding="utf-8")
    )

    assert packet["status"] == "pass"
    assert packet["screenshot_count"] == 44
    assert packet["coverage_complete"] is True
    screenshots = packet["screenshots"]
    assert isinstance(screenshots, list)
    assert screenshots[0].keys() >= {
        "route",
        "project",
        "viewport",
        "browser",
        "browser_version",
        "file",
        "sha256",
    }
    assert packet["workflow"]["workflow_url"].endswith("/actions/runs/123")  # type: ignore[index,union-attr]
    assert not list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(packet)
    )


def test_dashboard_packet_fails_when_tests_or_coverage_fail(tmp_path: Path) -> None:
    failed_report = tmp_path / "failed"
    _write_reports(failed_report, failed=True)
    assert build_packet(failed_report, "b" * 40)["status"] == "fail"

    incomplete_report = tmp_path / "incomplete"
    _write_reports(incomplete_report, omit_pair=True)
    packet = build_packet(incomplete_report, "b" * 40)
    assert packet["status"] == "fail"
    assert packet["coverage_complete"] is False


def test_dashboard_packet_fails_closed_without_structured_reports(tmp_path: Path) -> None:
    packet = build_packet(tmp_path / "missing", "b" * 40)

    assert packet["status"] == "missing_artifacts"
    assert packet["screenshot_count"] == 0
    assert packet["report_error"]


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

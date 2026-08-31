from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from reimburse_atlas.governance_monitoring import build_governance_monitor_report
from scripts import make_typescript_compatibility_report as compatibility
from scripts.make_typescript_compatibility_report import build_report


def _package(root: Path) -> None:
    path = root / "apps" / "dashboard" / "package.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps({"dependencies": {"@astrojs/check": "0.9.9", "typescript": "6.0.3"}}),
        encoding="utf-8",
    )


def test_typescript7_canary_blocks_on_checker_peer_range(tmp_path: Path) -> None:
    _package(tmp_path)

    def view(spec: str, field: str) -> tuple[object, str | None]:
        if field == "peerDependencies":
            return {"typescript": "^5.0.0 || ^6.0.0"}, None
        return ("7.0.2" if spec == "typescript@7" else ["5.9.3", "6.0.3"]), None

    report = build_report(tmp_path, npm_view=view)
    assert report["status"] == "blocked_peer"
    assert report["upgrade_recommended"] is False
    assert report["mutation_performed"] is False


def test_typescript7_canary_identifies_reviewable_upgrade(tmp_path: Path) -> None:
    _package(tmp_path)

    def view(_spec: str, field: str) -> tuple[object, str | None]:
        if field == "peerDependencies":
            return {"typescript": "^6.0.0 || ^7.0.0"}, None
        return "7.0.2", None

    report = build_report(tmp_path, npm_view=view)
    assert report["status"] == "upgrade_available"
    assert report["upgrade_recommended"] is True


def test_typescript7_canary_redacts_lookup_errors_to_summaries(tmp_path: Path) -> None:
    _package(tmp_path)

    def view(_spec: str, _field: str) -> tuple[object, str | None]:
        return None, "registry unavailable"

    report = build_report(tmp_path, npm_view=view)
    assert report["status"] == "blocked_network"
    assert report["mutation_performed"] is False
    assert report["errors"] == ["registry unavailable", "registry unavailable"]


@pytest.mark.parametrize(
    ("peer", "admitted", "expected"),
    [
        ("5.*", ["5.9.3"], "blocked_peer"),
        (">=7 <7", [], "blocked_peer"),
        (">=70", ["70.0.0"], "blocked_peer"),
        ("^7.2.0", ["7.2.0"], "blocked_peer"),
        (">7", ["8.0.0"], "blocked_peer"),
        (">=6 <8", ["6.0.3", "7.0.2"], "upgrade_available"),
        ("7.0.2", "7.0.2", "upgrade_available"),
        (">=7", ["7.0.2", "8.0.0"], "upgrade_available"),
        ("*", ["5.9.3", "7.0.2"], "upgrade_available"),
        ("^5 || ^6", ["5.9.3", "6.0.3"], "blocked_peer"),
        ("^6.0.0 || ^7.0.0", "7.0.2", "upgrade_available"),
        ("7.0.0 - 7.9.0", "7.0.2", "upgrade_available"),
        ("7.x", "7.0.2", "upgrade_available"),
        ("~7.0.0", "7.0.2", "upgrade_available"),
        ("v7.0.2", "7.0.2", "upgrade_available"),
        ("^5.0.0||^6.0.0", ["5.9.3", "6.0.3"], "blocked_peer"),
        (">= 6.0.0 < 8.0.0", "7.0.2", "upgrade_available"),
        ("7.0.X", "7.0.2", "upgrade_available"),
        ("7.*.*", "7.0.2", "upgrade_available"),
        ("7 - 8", "7.0.2", "upgrade_available"),
        ("x", "7.0.2", "upgrade_available"),
    ],
)
def test_range_is_resolved_by_npm_and_intersected_with_observed_candidates(
    tmp_path: Path,
    peer: str,
    admitted: object,
    expected: str,
) -> None:
    _package(tmp_path)
    calls: list[tuple[str, str]] = []

    def view(spec: str, field: str) -> tuple[object, str | None]:
        calls.append((spec, field))
        if field == "peerDependencies":
            return {"typescript": peer}, None
        return ("7.0.2" if spec == "typescript@7" else admitted), None

    report = build_report(tmp_path, npm_view=view)
    assert report["status"] == expected
    assert report["upgrade_recommended"] is (expected == "upgrade_available")
    assert calls == [
        ("@astrojs/check@0.9.9", "peerDependencies"),
        ("typescript@7", "version"),
        (f"typescript@{peer}", "version"),
    ]


def test_only_intersection_is_recommended(tmp_path: Path) -> None:
    _package(tmp_path)

    def view(spec: str, field: str) -> tuple[object, str | None]:
        if field == "peerDependencies":
            return {"typescript": ">=7.1 <8"}, None
        return (["7.0.2", "7.1.0", "7.1.0"] if spec == "typescript@7" else "7.1.0"), None

    report = build_report(tmp_path, npm_view=view)
    assert report["status"] == "upgrade_available"
    assert report["candidate_typescript7"] == "7.1.0"


@pytest.mark.parametrize("value", [None, "", {}, 7, ["7.0.2", None], "7.0.2-beta.1", "07.0.2"])
@pytest.mark.parametrize("invalid_query", ["candidate", "peer"])
def test_malformed_version_metadata_fails_closed(
    tmp_path: Path,
    value: object,
    invalid_query: str,
) -> None:
    _package(tmp_path)

    def view(spec: str, field: str) -> tuple[object, str | None]:
        if field == "peerDependencies":
            return {"typescript": "^7.0.0"}, None
        query = "candidate" if spec == "typescript@7" else "peer"
        return (value if query == invalid_query else "7.0.2"), None

    report = build_report(tmp_path, npm_view=view)
    assert report["status"] == "unknown"
    assert report["upgrade_recommended"] is False


@pytest.mark.parametrize("candidate", [[], "8.0.0", ["7.0.2", "8.0.0"]])
def test_unavailable_or_non_seven_channel_fails_closed(tmp_path: Path, candidate: object) -> None:
    _package(tmp_path)

    def view(spec: str, field: str) -> tuple[object, str | None]:
        if field == "peerDependencies":
            return {"typescript": "*"}, None
        assert spec == "typescript@7"
        return candidate, None

    report = build_report(tmp_path, npm_view=view)
    assert report["status"] == "unknown"
    assert report["upgrade_recommended"] is False


@pytest.mark.parametrize("peer", [None, "", " ", 7, ["^7"]])
def test_missing_or_malformed_peer_does_not_query_a_range(tmp_path: Path, peer: object) -> None:
    _package(tmp_path)

    def view(spec: str, field: str) -> tuple[object, str | None]:
        if field == "peerDependencies":
            return {"typescript": peer}, None
        assert spec == "typescript@7"
        return "7.0.2", None

    report = build_report(tmp_path, npm_view=view)
    assert report["status"] == "unknown"
    assert report["upgrade_recommended"] is False


@pytest.mark.parametrize(
    "peer",
    [
        "file:/tmp/pkg",
        "/example/pkg",
        "../pkg",
        "git+https://example.invalid/typescript.git",
        "git://example.invalid/typescript.git",
        "https://example.invalid/typescript.tgz",
        "typescript-7.0.2.tgz",
        "npm:other-package@7",
        "--registry=https://example.invalid",
        "--7",
        "",
        "latest",
        "beta7",
        "^7.0.0-beta.1",
        "7.0.0+build.1",
        "^\u0667.0.0",
        "7\u00a0-\u00a08",
        "7" * 513,
        "x7",
        "xx",
        "x-7",
        "7-7",
        "07",
        "7.01",
        "7.0.02",
        "v07.0.0",
        "V7.0.0",
        "vX",
        "vx",
        "x.7",
        "7.x.1",
        "7.0.0.1",
        "^~7",
        "=>7",
        "!=7",
        "7 ||",
        "|| 7",
        "7 | 8",
        "7 || || 8",
        "^7 - 8",
        "7 -8",
        "7- 8",
        "unknown7",
        "7foo",
        "9007199254740992",
        "9007199254740991",
    ],
)
def test_unsupported_peer_spec_is_unknown_without_third_lookup(tmp_path: Path, peer: str) -> None:
    _package(tmp_path)
    calls: list[tuple[str, str]] = []

    def view(spec: str, field: str) -> tuple[object, str | None]:
        calls.append((spec, field))
        if field == "peerDependencies":
            return {"typescript": peer}, None
        assert spec == "typescript@7"
        return "7.0.2", None

    report = build_report(tmp_path, npm_view=view)
    assert report["status"] == "unknown"
    assert report["upgrade_recommended"] is False
    assert calls == [("@astrojs/check@0.9.9", "peerDependencies"), ("typescript@7", "version")]


@pytest.mark.parametrize(
    ("error", "status"),
    [("registry unavailable", "blocked_network"), ("npm metadata lookup timed out", "unknown")],
)
def test_peer_query_failure_never_recommends_upgrade(
    tmp_path: Path,
    error: str,
    status: str,
) -> None:
    _package(tmp_path)

    def view(spec: str, field: str) -> tuple[object, str | None]:
        if field == "peerDependencies":
            return {"typescript": "^7"}, None
        return ("7.0.2", None) if spec == "typescript@7" else (None, error)

    report = build_report(tmp_path, npm_view=view)
    assert report["status"] == status
    assert report["upgrade_recommended"] is False
    assert report["errors"] == [error]


def test_range_query_uses_fixed_argv_and_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _package(tmp_path)
    calls: list[list[str]] = []

    def run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        assert kwargs == {
            "cwd": tmp_path / "apps/dashboard",
            "capture_output": True,
            "check": False,
            "text": True,
            "timeout": 60,
        }
        value: object = {"typescript": ">=6 <8 || ^9"} if argv[3] == "peerDependencies" else "7.0.2"
        return subprocess.CompletedProcess(argv, 0, json.dumps(value), "")

    monkeypatch.setattr(compatibility.subprocess, "run", run)
    assert build_report(tmp_path)["status"] == "upgrade_available"
    assert calls[-1] == ["npm", "view", "typescript@>=6 <8 || ^9", "version", "--json"]


@pytest.mark.parametrize("status", ["unknown", "blocked_network", "blocked_peer"])
def test_inconclusive_canary_remains_external_not_release_blocking(status: str) -> None:
    report = build_governance_monitor_report(typescript_report={"status": status}, github_report={})
    record = next(row for row in report.records if row.id == "typescript7_astro_compatibility")
    assert record.status == "blocked_external"
    assert record.required_for_repository_release is False
    assert report.summary.repository_release_blocker_count == 0


@pytest.mark.parametrize(
    ("output", "returncode", "stderr", "expected"),
    [
        ("", 0, "", "unknown"),
        ("[]", 0, "", "blocked_peer"),
        ('"7.0.2-beta.1"', 0, "", "unknown"),
        ('["7.0.2", "7.0.3-beta.1"]', 0, "", "unknown"),
        ('"7.0.2+build.1"', 0, "", "unknown"),
        ('"7.0.2"', 1, "npm error E404 No match found for version", "blocked_network"),
    ],
)
def test_native_npm_range_response_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    output: str,
    returncode: int,
    stderr: str,
    expected: str,
) -> None:
    _package(tmp_path)

    def run(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        if argv[3] == "peerDependencies":
            return subprocess.CompletedProcess(argv, 0, '{"typescript": "^7"}', "")
        if argv[2] == "typescript@7":
            return subprocess.CompletedProcess(argv, 0, '"7.0.2"', "")
        assert argv == ["npm", "view", "typescript@^7", "version", "--json"]
        return subprocess.CompletedProcess(argv, returncode, output, stderr)

    monkeypatch.setattr(compatibility.subprocess, "run", run)
    report = build_report(tmp_path)
    assert report["status"] == expected
    assert report["upgrade_recommended"] is False
    assert report["mutation_performed"] is False
    if returncode:
        assert report["errors"] == [stderr]

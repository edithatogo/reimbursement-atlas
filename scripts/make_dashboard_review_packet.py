"""Build commit-bound dashboard evidence from structured Playwright reports."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

from defusedxml import ElementTree as ET

from reimburse_atlas.dashboard_review import dashboard_source_fingerprint
from reimburse_atlas.registry import project_root

ROUTES = (
    "/",
    "/analyses/",
    "/analyses/cognitive_vs_procedural_ratio/",
    "/automation/",
    "/crosswalks/",
    "/demonstrators/",
    "/ontologies/",
    "/readiness/",
    "/roadmap/",
    "/sources/",
    "/sources/au_mbs/",
)
PROJECTS = (
    "desktop-chromium",
    "mobile-chromium",
    "desktop-firefox",
    "desktop-webkit",
)
EXPECTED_TEST_COUNT = 64


class GitHeadResolutionError(ValueError):
    """Raised when the dashboard packet cannot resolve the tested commit."""


class ReportEvidenceError(ValueError):
    """Raised when structured browser evidence is absent or malformed."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _iter_specs(suites: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    for suite in suites:
        yield from cast("list[dict[str, Any]]", suite.get("specs", []))
        yield from _iter_specs(cast("list[dict[str, Any]]", suite.get("suites", [])))


def _attachment_bytes(attachment: dict[str, Any], report_dir: Path) -> tuple[bytes, str]:
    if body := attachment.get("body"):
        try:
            return base64.b64decode(cast("str", body), validate=True), "embedded"
        except ValueError as error:
            raise ReportEvidenceError from error
    raw_path = attachment.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise ReportEvidenceError
    path = Path(raw_path)
    candidates = (path, report_dir / path, report_dir.parent / path)
    resolved = next((candidate for candidate in candidates if candidate.is_file()), None)
    if resolved is None:
        raise ReportEvidenceError
    return resolved.read_bytes(), resolved.name


def _parse_context(attachment: dict[str, Any], report_dir: Path) -> dict[str, Any]:
    body, _ = _attachment_bytes(attachment, report_dir)
    try:
        value = json.loads(body)
    except json.JSONDecodeError as error:
        raise ReportEvidenceError from error
    if not isinstance(value, dict):
        raise ReportEvidenceError
    return cast("dict[str, Any]", value)


def _junit_summary(path: Path) -> dict[str, int]:
    if not path.is_file():
        raise ReportEvidenceError
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        raise ReportEvidenceError from error
    if root is None:
        raise ReportEvidenceError
    suites = [root] if root.tag == "testsuite" else list(root.findall(".//testsuite"))
    if not suites:
        raise ReportEvidenceError
    top = suites if root.tag == "testsuite" else list(root.findall("./testsuite"))
    counted = top or suites
    return {
        key: sum(int(suite.attrib.get(key, "0")) for suite in counted)
        for key in ("tests", "failures", "errors", "skipped")
    }


def _workflow_metadata() -> dict[str, object]:
    server = os.environ.get("GITHUB_SERVER_URL")
    repository = os.environ.get("GITHUB_REPOSITORY")
    run_id = os.environ.get("GITHUB_RUN_ID")
    workflow_url = (
        f"{server}/{repository}/actions/runs/{run_id}" if server and repository and run_id else None
    )
    return {
        "workflow": os.environ.get("GITHUB_WORKFLOW"),
        "run_id": run_id,
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "artifact_name": f"dashboard-browser-review-{run_id}" if run_id else None,
        "workflow_url": workflow_url,
    }


def _route_screenshot(
    test: dict[str, Any], report_dir: Path
) -> tuple[str, dict[str, object] | None]:
    project = cast("str", test.get("projectName"))
    results = cast("list[dict[str, Any]]", test.get("results", []))
    final = results[-1] if results else {}
    status = cast("str", final.get("status", "missing"))
    attachments = cast("list[dict[str, Any]]", final.get("attachments", []))
    screenshot = next(
        (item for item in attachments if item.get("name") == "route-screenshot"), None
    )
    context_attachment = next(
        (item for item in attachments if item.get("name") == "dashboard-review-context"), None
    )
    if screenshot is None and context_attachment is None:
        return status, None
    if screenshot is None or context_attachment is None:
        raise ReportEvidenceError
    context = _parse_context(context_attachment, report_dir)
    image, filename = _attachment_bytes(screenshot, report_dir)
    if context.get("project") != project:
        raise ReportEvidenceError
    return status, {
        "route": context.get("route"),
        "project": project,
        "viewport": context.get("viewport"),
        "browser": context.get("browser"),
        "browser_version": context.get("browserVersion"),
        "file": filename,
        "sha256": _sha256_bytes(image),
        "byte_size": len(image),
    }


def _parse_reports(
    report_dir: Path,
) -> tuple[list[dict[str, object]], list[str], dict[str, int]]:
    report = cast(
        "dict[str, Any]",
        json.loads((report_dir / "results.json").read_text(encoding="utf-8")),
    )
    screenshots: list[dict[str, object]] = []
    statuses: list[str] = []
    for spec in _iter_specs(cast("list[dict[str, Any]]", report.get("suites", []))):
        for test in cast("list[dict[str, Any]]", spec.get("tests", [])):
            status, screenshot = _route_screenshot(test, report_dir)
            statuses.append(status)
            if screenshot is not None:
                screenshots.append(screenshot)
    return screenshots, statuses, _junit_summary(report_dir / "results.xml")


def _coverage_complete(screenshots: list[dict[str, object]]) -> bool:
    expected = {(route, project) for route in ROUTES for project in PROJECTS}
    observed = {(cast("str", row["route"]), cast("str", row["project"])) for row in screenshots}
    return observed == expected and len(screenshots) == len(expected)


def _tests_passed(statuses: list[str], junit: dict[str, int]) -> bool:
    return (
        len(statuses) == EXPECTED_TEST_COUNT
        and all(status == "passed" for status in statuses)
        and junit == {"tests": EXPECTED_TEST_COUNT, "failures": 0, "errors": 0, "skipped": 0}
    )


def build_packet(
    report_dir: Path,
    tested_commit: str,
    *,
    source_fingerprint: str | None = None,
) -> dict[str, object]:
    """Build a fail-closed packet from Playwright JSON, JUnit, and attachments."""
    try:
        screenshots, statuses, junit = _parse_reports(report_dir)
    except (OSError, json.JSONDecodeError, ReportEvidenceError, KeyError, TypeError) as caught:
        return _packet(
            tested_commit=tested_commit,
            status="missing_artifacts",
            screenshots=[],
            test_count=0,
            junit={"tests": 0, "failures": 0, "errors": 0, "skipped": 0},
            coverage_complete=False,
            report_error=str(caught) or type(caught).__name__,
            source_fingerprint=source_fingerprint,
        )
    coverage_complete = _coverage_complete(screenshots)
    status = "pass" if _tests_passed(statuses, junit) and coverage_complete else "fail"
    return _packet(
        tested_commit=tested_commit,
        status=status,
        screenshots=screenshots,
        test_count=len(statuses),
        junit=junit,
        coverage_complete=coverage_complete,
        report_error=None,
        source_fingerprint=source_fingerprint,
    )


def _packet(
    *,
    tested_commit: str,
    status: str,
    screenshots: list[dict[str, object]],
    test_count: int,
    junit: dict[str, int],
    coverage_complete: bool,
    report_error: str | None,
    source_fingerprint: str | None,
) -> dict[str, object]:
    return {
        "schema_version": "dashboard-automated-review-v2",
        "status": status,
        "tested_commit": tested_commit,
        "source_fingerprint": source_fingerprint,
        "test_count": test_count,
        "expected_test_count": EXPECTED_TEST_COUNT,
        "junit": junit,
        "routes": list(ROUTES),
        "projects": list(PROJECTS),
        "route_count": len(ROUTES),
        "project_count": len(PROJECTS),
        "coverage_complete": coverage_complete,
        "screenshot_count": len(screenshots),
        "screenshots": sorted(
            screenshots,
            key=lambda item: (cast("str", item["route"]), cast("str", item["project"])),
        ),
        "workflow": _workflow_metadata(),
        "report_error": report_error,
        "automated_scope": [
            "axe violations",
            "keyboard search and focus",
            "route response and semantics",
            "responsive browser matrix",
            "performance budgets",
            "console and page errors",
            "table captions",
        ],
        "human_review_required": True,
    }


def resolve_head(root: Path) -> str:
    """Resolve the tested commit without invoking a subprocess."""
    if github_sha := os.environ.get("GITHUB_SHA"):
        return github_sha

    dot_git = root / ".git"
    if dot_git.is_file():
        marker = dot_git.read_text(encoding="utf-8").strip()
        if not marker.startswith("gitdir: "):
            raise GitHeadResolutionError
        git_dir = (root / marker.removeprefix("gitdir: ")).resolve()
    else:
        git_dir = dot_git

    head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
    if not head.startswith("ref: "):
        return head
    ref = head.removeprefix("ref: ")
    git_dirs = [git_dir]
    common_dir_marker = git_dir / "commondir"
    if common_dir_marker.is_file():
        common_dir = (git_dir / common_dir_marker.read_text(encoding="utf-8").strip()).resolve()
        git_dirs.append(common_dir)
    for candidate_dir in git_dirs:
        loose_ref = candidate_dir / ref
        if loose_ref.is_file():
            return loose_ref.read_text(encoding="utf-8").strip()
        packed_refs = candidate_dir / "packed-refs"
        if not packed_refs.is_file():
            continue
        for line in packed_refs.read_text(encoding="utf-8").splitlines():
            if line and not line.startswith(("#", "^")):
                commit, packed_ref = line.split(" ", maxsplit=1)
                if packed_ref == ref:
                    return commit
    raise GitHeadResolutionError(ref)


def main() -> None:
    """Write the local dashboard automated-review packet."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-dir", type=Path, default=Path("apps/test-results"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/derived/dashboard_review/automated_review_packet.json"),
    )
    args = parser.parse_args()
    root = project_root()
    packet = build_packet(
        root / args.report_dir,
        resolve_head(root),
        source_fingerprint=dashboard_source_fingerprint(root),
    )
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: packet[key] for key in ("status", "tested_commit", "screenshot_count")},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

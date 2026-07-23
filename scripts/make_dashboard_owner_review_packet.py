"""Build one bounded dashboard packet for accountable scoped review."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.dashboard_review import dashboard_source_fingerprint
from reimburse_atlas.registry import project_root
from scripts.make_dashboard_review_packet import PROJECTS, ROUTES, resolve_head

AUTOMATED = Path("data/derived/dashboard_review/automated_review_packet.json")
OUTPUT = Path("data/derived/dashboard_review/owner_review_packet.json")
PROVENANCE_INPUTS = (
    Path("apps/dashboard/public/status.json"),
    Path("data/derived/source_validation/summary.json"),
    Path("data/derived/evidence_readiness/summary.json"),
    Path("data/derived/release_readiness/summary.json"),
    Path("data/derived/publication_manifest.json"),
)
PROHIBITED_PATTERNS = {
    "raw_live_path": re.compile(r"(?:^|[/\\\\])data[/\\\\]raw_live(?:[/\\\\]|$)"),
    "local_absolute_path": re.compile(r"(?:/Users/|/Volumes/|[A-Za-z]:\\\\Users\\\\)"),
    "secret_assignment": re.compile(
        r"(?i)(?:token|api[_-]?key|subscription[_-]?key|password)\s*[:=]\s*"
        r"[\"']?[A-Za-z0-9_./+=-]{12,}"
    ),
}
TEXT_SUFFIXES = {".csv", ".html", ".json", ".jsonl", ".md", ".txt", ".xml"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return cast("dict[str, Any]", value) if isinstance(value, dict) else {}


def _value_at(value: dict[str, Any], path: str) -> object:
    current: object = value
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = cast("dict[str, object]", current).get(part)
    return current


def _provenance_assertions(root: Path) -> list[dict[str, object]]:
    status = _read_json(root / "apps/dashboard/public/status.json")
    checks = (
        (
            "source-validation-status",
            "evidence.source_validation",
            Path("data/derived/source_validation/summary.json"),
            "status",
        ),
        (
            "evidence-release-readiness",
            "evidence.evidence_release_ready",
            Path("data/derived/release_readiness/summary.json"),
            "evidence_release_ready",
        ),
        (
            "repository-release-readiness",
            "software.repository_release_ready",
            Path("data/derived/release_readiness/summary.json"),
            "repository_release_ready",
        ),
        (
            "research-publication-readiness",
            "evidence.research_publication_ready",
            Path("data/derived/release_readiness/summary.json"),
            "research_publication_ready",
        ),
    )
    assertions: list[dict[str, object]] = []
    for identifier, displayed_path, source_path, source_field in checks:
        source = _read_json(root / source_path)
        displayed = _value_at(status, displayed_path)
        expected = _value_at(source, source_field)
        if identifier == "source-validation-status" and expected is None:
            failures = source.get("blocking_failures")
            expected = "pass" if failures == 0 else "blocked" if isinstance(failures, int) else None
        assertions.append({
            "id": identifier,
            "displayed_path": f"apps/dashboard/public/status.json#{displayed_path}",
            "source_path": source_path.as_posix(),
            "source_field": source_field,
            "displayed_value": displayed,
            "expected_value": expected,
            "status": "pass" if displayed == expected and expected is not None else "fail",
        })
    return assertions


def _prohibited_content_check(root: Path) -> dict[str, object]:
    public_root = root / "apps/dashboard/public"
    findings: list[dict[str, str]] = []
    files_checked = 0
    for path in sorted(public_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        files_checked += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for identifier, pattern in PROHIBITED_PATTERNS.items():
            if match := pattern.search(text):
                findings.append({
                    "rule": identifier,
                    "path": path.relative_to(root).as_posix(),
                    "match_sha256": hashlib.sha256(match.group(0).encode("utf-8")).hexdigest(),
                })
    return {
        "status": "pass" if not findings else "fail",
        "files_checked": files_checked,
        "rules": sorted(PROHIBITED_PATTERNS),
        "findings": findings,
    }


def build_packet(root: Path) -> dict[str, Any]:
    """Return deterministic evidence and a bounded accountable-review checklist."""
    automated = _read_json(root / AUTOMATED)
    current_head = resolve_head(root)
    source_fingerprint = dashboard_source_fingerprint(root)
    provenance = [
        {
            "path": path.as_posix(),
            "sha256": _sha256(root / path),
            "byte_size": (root / path).stat().st_size,
        }
        for path in PROVENANCE_INPUTS
        if (root / path).is_file()
    ]
    provenance_assertions = _provenance_assertions(root)
    prohibited_content = _prohibited_content_check(root)
    screenshot_evidence = cast("list[dict[str, Any]]", automated.get("screenshots", []))
    routes = cast("list[str]", automated.get("routes", []))
    projects = cast("list[str]", automated.get("projects", []))
    machine_ready = (
        automated.get("status") == "pass"
        and automated.get("coverage_complete") is True
        and automated.get("source_fingerprint") == source_fingerprint
        and routes == list(ROUTES)
        and projects == list(PROJECTS)
        and len(screenshot_evidence) == len(ROUTES) * len(PROJECTS)
        and all(assertion["status"] == "pass" for assertion in provenance_assertions)
        and prohibited_content["status"] == "pass"
    )
    return {
        "schema_version": "dashboard-owner-review-packet-v2",
        "status": ("pending_accountable_review" if machine_ready else "automated_evidence_blocked"),
        "tested_commit": automated.get("tested_commit"),
        "current_head": current_head,
        "source_fingerprint": source_fingerprint,
        "commit_parity": automated.get("tested_commit") == current_head,
        "review_target_parity": automated.get("source_fingerprint") == source_fingerprint,
        "automated_status": automated.get("status", "missing"),
        "workflow": automated.get("workflow", {}),
        "routes": routes,
        "browser_projects": projects,
        "route_coverage_bounded": routes == list(ROUTES),
        "automated_test_count": automated.get("test_count", 0),
        "screenshot_count": len(screenshot_evidence),
        "screenshots": screenshot_evidence,
        "provenance_inputs": provenance,
        "provenance_assertions": provenance_assertions,
        "prohibited_content_check": prohibited_content,
        "accountable_checklist": [
            "Inspect visual hierarchy, clipping and responsive layout on every listed route.",
            "Complete keyboard-only navigation and confirm visible focus and skip navigation.",
            "Complete macOS VoiceOver review in Safari and record the exact versions.",
            (
                "Spot-check displayed source, version, checksum, licence and readiness values "
                "against the structured provenance assertions."
            ),
            "Confirm no raw or restricted source content is exposed.",
            "Record every finding, remediation or bounded waiver.",
            "Use approved_within_scope only; do not claim universal WCAG conformance.",
        ],
        "required_record": "data/derived/dashboard_review/human_review.json",
        "record_schema": "schema/DashboardHumanReviewRecord.schema.json",
    }


def main() -> None:
    """Write the bounded accountable-review packet."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Replace the tracked packet after ingesting fresh commit-bound browser evidence.",
    )
    args = parser.parse_args()
    root = project_root()
    output = root / OUTPUT
    if output.is_file() and not args.refresh:
        existing = _read_json(output)
        print(
            json.dumps(
                {
                    "status": existing.get("status", "missing"),
                    "tested_commit": existing.get("tested_commit"),
                    "preserved": True,
                    "reason": "explicit_refresh_required",
                },
                indent=2,
            )
        )
        return
    packet = build_packet(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": packet["status"],
                "tested_commit": packet["tested_commit"],
                "commit_parity": packet["commit_parity"],
                "routes": len(cast("list[str]", packet["routes"])),
                "provenance_inputs": len(cast("list[dict[str, Any]]", packet["provenance_inputs"])),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

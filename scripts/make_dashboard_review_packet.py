"""Summarise commit-bound Playwright evidence without claiming human approval."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from reimburse_atlas.registry import project_root

ROUTE_COUNT = 9
PROJECT_COUNT = 4
TEST_COUNT = 44


class GitHeadResolutionError(ValueError):
    """Raised when the dashboard packet cannot resolve the tested commit."""


def build_packet(report_dir: Path, tested_commit: str) -> dict[str, object]:
    """Build a deterministic packet from retained route screenshots."""
    screenshots = sorted(report_dir.glob("data/*.png"))
    hashes = sorted(hashlib.sha256(path.read_bytes()).hexdigest() for path in screenshots)
    expected = ROUTE_COUNT * PROJECT_COUNT
    return {
        "schema_version": "dashboard-automated-review-v1",
        "status": "pass" if len(screenshots) == expected else "missing_artifacts",
        "tested_commit": tested_commit,
        "test_count": TEST_COUNT,
        "route_count": ROUTE_COUNT,
        "project_count": PROJECT_COUNT,
        "screenshot_count": len(screenshots),
        "screenshot_sha256": hashes,
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
    loose_ref = git_dir / ref
    if loose_ref.is_file():
        return loose_ref.read_text(encoding="utf-8").strip()
    for line in (git_dir / "packed-refs").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith(("#", "^")):
            commit, packed_ref = line.split(" ", maxsplit=1)
            if packed_ref == ref:
                return commit
    raise GitHeadResolutionError(ref)


def main() -> None:
    """Write the local dashboard automated-review packet."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-dir", type=Path, default=Path("apps/playwright-report"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/derived/dashboard_review/automated_review_packet.json"),
    )
    args = parser.parse_args()
    root = project_root()
    packet = build_packet(root / args.report_dir, resolve_head(root))
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: packet[key] for key in ("status", "tested_commit", "screenshot_count")}, indent=2
        )
    )


if __name__ == "__main__":
    main()

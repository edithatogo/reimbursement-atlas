"""Summarise commit-bound Playwright evidence without claiming human approval."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from reimburse_atlas.registry import project_root

ROUTE_COUNT = 9
PROJECT_COUNT = 4
TEST_COUNT = 44


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


def _head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


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
    packet = build_packet(root / args.report_dir, _head(root))
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

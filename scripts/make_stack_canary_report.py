"""Build a stack-canary summary and issue body from dashboard drift output."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast


def main() -> None:
    """Write a structured canary summary plus a human-readable issue body."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-json", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    parser.add_argument("--issue-body", type=Path, required=True)
    args = parser.parse_args()

    raw: dict[str, dict[str, Any]] = (
        cast("dict[str, dict[str, Any]]", json.loads(args.raw_json.read_text(encoding="utf-8")))
        if args.raw_json.exists()
        else {}
    )
    entries: list[dict[str, Any]] = []
    for name, value in raw.items():
        entries.append({
            "name": name,
            "current": value.get("current"),
            "wanted": value.get("wanted"),
            "latest": value.get("latest"),
            "location": value.get("location"),
        })
    summary: dict[str, Any] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dashboard_dependency_drift_count": len(entries),
        "dashboard_dependency_drift": entries,
        "dashboard_dependencies_current": not entries,
    }
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    body_lines = [
        "# Stack canary drift",
        "",
        "The scheduled canary detected one or more dependency/runtime updates.",
        "",
        "## Summary",
        "",
        f"- Generated at: {summary['generated_at']}",
        f"- Drift count: {summary['dashboard_dependency_drift_count']}",
        "",
        "## Drift",
        "",
    ]
    body_lines.extend(
        (
            f"- {item['name']}: current={item['current']} "
            f"wanted={item['wanted']} latest={item['latest']}"
        )
        for item in entries
    )
    args.issue_body.write_text("\n".join(body_lines).rstrip() + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_json": str(args.summary_json),
                "issue_body": str(args.issue_body),
                "drift_count": len(entries),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

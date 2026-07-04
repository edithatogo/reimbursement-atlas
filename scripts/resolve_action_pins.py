"""Resolve tag-pinned GitHub Actions to immutable commit SHAs when network permits."""

from __future__ import annotations

import json

from reimburse_atlas.action_pins import resolve_action_pins
from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.registry import project_root


def main() -> None:
    """Write action-pin resolution evidence."""
    root = project_root()
    output_dir = root / "data" / "derived" / "repo_automation"
    output_dir.mkdir(parents=True, exist_ok=True)
    records = [record.as_row() for record in resolve_action_pins(root)]
    write_jsonl(records, output_dir / "action_pin_resolution.jsonl")
    write_csv(records, output_dir / "action_pin_resolution.csv")
    summary: dict[str, int] = {}
    for row in records:
        status = str(row["status"])
        summary[status] = summary.get(status, 0) + 1
    (output_dir / "action_pin_resolution_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"records": len(records), "summary": summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

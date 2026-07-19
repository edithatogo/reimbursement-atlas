"""Invalidate checksum-bound approvals whose candidate artefacts changed."""

from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.registry import project_root


def reconcile(root: Path | None = None) -> int:
    """Update stale decisions to blocked using the current queue checksum."""
    repo = root or project_root()
    queue_path = repo / "data/derived/licence_review/licence_review_queue.jsonl"
    decisions_path = repo / "data/licence_review/decisions.jsonl"
    queue = {
        row["relative_path"]: row
        for row in (
            json.loads(line)
            for line in queue_path.read_text(encoding="utf-8").splitlines()
        )
        if row.get("relative_path")
    }
    changed = 0
    output: list[str] = []
    for line in decisions_path.read_text(encoding="utf-8").splitlines():
        decision = json.loads(line)
        current = queue.get(decision.get("relative_path"))
        if current and decision.get("checksum_sha256") != current["checksum_sha256"]:
            decision["checksum_sha256"] = current["checksum_sha256"]
            decision["decision"] = "blocked"
            decision["evidence"] = (
                "Prior checksum-bound approval invalidated by deterministic candidate "
                "change; re-review required for the new checksum."
            )
            decision["redistribution_permission"] = (
                "Not approved for publication until the new checksum is reviewed."
            )
            changed += 1
        output.append(json.dumps(decision, separators=(",", ":"), sort_keys=True))
    decisions_path.write_text("\n".join(output) + "\n", encoding="utf-8")
    return changed


if __name__ == "__main__":
    print(f"Invalidated {reconcile()} stale checksum-bound licence decisions")

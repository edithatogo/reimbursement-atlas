"""Invalidate checksum-bound approvals whose candidate artefacts changed."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from reimburse_atlas.registry import project_root


def reconcile(root: Path | None = None) -> int:
    """Reconcile decisions with the queue, failing closed for new candidates."""
    repo = root or project_root()
    queue_path = repo / "data/derived/licence_review/licence_review_queue.jsonl"
    decisions_path = repo / "data/licence_review/decisions.jsonl"
    queue = {
        row["relative_path"]: row
        for row in (
            json.loads(line) for line in queue_path.read_text(encoding="utf-8").splitlines()
        )
        if row.get("relative_path")
    }
    changed = 0
    decisions: dict[str, dict[str, object]] = {}
    output: list[str] = []
    for line in decisions_path.read_text(encoding="utf-8").splitlines():
        decision = json.loads(line)
        current = queue.get(decision.get("relative_path"))
        if current is None:
            # The active ledger contains only artefacts that require source-rights
            # review. Project-owned metadata is governed by the code licence.
            changed += 1
            continue
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
        decisions[str(decision["relative_path"])] = decision

    # Keep the human ledger total with the generated queue. New candidates must
    # be explicit blockers, never silently absent or implicitly approved.
    reviewed_at = datetime.now(UTC).date().isoformat()
    for path, current in queue.items():
        if path in decisions:
            continue
        decisions[path] = {
            "attribution": (
                "Reimbursement Atlas project-owned or source-derived artefact; retain "
                "applicable provider attribution recorded in the source registry and "
                "provenance manifest."
            ),
            "checksum_sha256": current["checksum_sha256"],
            "decision": "blocked",
            "evidence": (
                "New generated publication candidate has no human licence decision; "
                "checksum-bound review is required before publication consideration."
            ),
            "redistribution_permission": (
                "Not approved for publication until this checksum is reviewed."
            ),
            "relative_path": path,
            "restrictions": current.get("restrictions")
            or (
                "Exclude raw source payloads, credentials, request headers, restricted "
                "descriptors, confidential values, unsupported coverage/net-price claims "
                "and source-specific fields not expressly permitted by applicable evidence."
            ),
            "review_id": current["review_id"],
            "reviewed_at": reviewed_at,
            "reviewer": "repository-owner",
            "source_terms": (
                "Licence review required; consult applicable provider terms and source "
                "evidence in the source registry, provenance manifest and review matrix."
            ),
        }
        changed += 1

    output = [
        json.dumps(decisions[path], separators=(",", ":"), sort_keys=True)
        for path in sorted(decisions)
    ]
    decisions_path.write_text("\n".join(output) + "\n", encoding="utf-8")
    return changed


if __name__ == "__main__":
    print(f"Invalidated {reconcile()} stale checksum-bound licence decisions")

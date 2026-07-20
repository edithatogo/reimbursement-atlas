"""Record explicit checksum-bound licence approvals from the generated queue."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from reimburse_atlas.registry import project_root


def record_approvals(
    paths: list[str],
    *,
    reviewer: str,
    approval_reference: str,
    root: Path | None = None,
) -> int:
    """Approve only named queue rows, binding each decision to its current checksum."""
    repo = root or project_root()
    queue_path = repo / "data/derived/licence_review/licence_review_queue.jsonl"
    decisions_path = repo / "data/licence_review/decisions.jsonl"
    queue = {
        row["relative_path"]: row
        for row in (
            json.loads(line)
            for line in queue_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    requested = set(paths)
    missing = sorted(requested - queue.keys())
    if missing:
        message = f"paths are not present in the current licence queue: {missing}"
        raise ValueError(message)

    decisions = [
        json.loads(line)
        for line in decisions_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    seen: set[str] = set()
    changed = 0
    reviewed_at = datetime.now(UTC).date().isoformat()
    for decision in decisions:
        path = decision.get("relative_path")
        if path not in requested:
            continue
        if path in seen:
            message = f"duplicate decision path: {path}"
            raise ValueError(message)
        seen.add(path)
        row = queue[path]
        if decision.get("checksum_sha256") != row["checksum_sha256"]:
            message = f"checksum mismatch before approval: {path}"
            raise ValueError(message)
        if row.get("contains_raw_source_payload") is True:
            message = f"raw source payload cannot be approved: {path}"
            raise ValueError(message)
        decision.update({
            "decision": "approved",
            "evidence": (
                f"Explicit repository-owner approval recorded in {approval_reference}; "
                "exact current candidate path and SHA-256 verified against the generated queue."
            ),
            "redistribution_permission": (
                "Approved only within the documented grouped scope: derived candidate fields "
                "within the approved grouped scope; no raw source payloads or restricted "
                "descriptors."
            ),
            "reviewer": reviewer,
            "reviewed_at": reviewed_at,
        })
        changed += 1

    if seen != requested:
        message = f"decisions missing for requested paths: {sorted(requested - seen)}"
        raise ValueError(message)
    decisions_path.write_text(
        "\n".join(json.dumps(row, separators=(",", ":"), sort_keys=True) for row in decisions)
        + "\n",
        encoding="utf-8",
    )
    return changed


def main() -> None:
    """Parse explicit approval arguments and update the decision record."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", action="append", required=True)
    parser.add_argument("--reviewer", default="repository-owner")
    parser.add_argument("--approval-reference", required=True)
    args = parser.parse_args()
    try:
        count = record_approvals(
            args.path,
            reviewer=args.reviewer,
            approval_reference=args.approval_reference,
        )
    except ValueError as error:
        parser.error(str(error))
    print(f"Recorded {count} checksum-bound licence approvals")


if __name__ == "__main__":
    main()

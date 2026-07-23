"""Freeze an exact mapping adjudication proposal after accountable approval."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.io import write_jsonl
from reimburse_atlas.mapping_study_paths import mapping_study_paths
from reimburse_atlas.registry import project_root


def _rows(path: Path) -> list[dict[str, Any]]:
    return [
        cast("dict[str, Any]", json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def approve(
    root: Path,
    *,
    cycle: str,
    proposal_sha256: str,
    reviewer: str,
    confirmation: str,
    approved_at: str,
) -> list[dict[str, Any]]:
    """Return immutable final adjudications only for the exact approved proposal."""
    paths = mapping_study_paths(cycle)
    proposal_path = root / paths.proposals
    actual_sha256 = hashlib.sha256(proposal_path.read_bytes()).hexdigest()
    if proposal_sha256 != actual_sha256:
        message = "approved proposal SHA-256 does not match the current proposal file"
        raise ValueError(message)
    if confirmation != f"APPROVE_MAPPING_ADJUDICATION:{actual_sha256}":
        message = "exact checksum-bound adjudication confirmation is required"
        raise ValueError(message)
    if not reviewer.strip():
        message = "accountable reviewer must be named"
        raise ValueError(message)
    timestamp = datetime.fromisoformat(approved_at)
    if timestamp.tzinfo is None:
        message = "approved-at must include a timezone"
        raise ValueError(message)
    return [
        {
            **row,
            "accountable_reviewer": reviewer.strip(),
            "accountable_approved_at": timestamp.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            "approved_proposal_sha256": actual_sha256,
        }
        for row in _rows(proposal_path)
    ]


def main() -> None:
    """Write final adjudications after exact accountable approval."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle", required=True)
    parser.add_argument("--proposal-sha256", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--confirm", required=True)
    parser.add_argument("--approved-at", required=True)
    args = parser.parse_args()
    root = project_root()
    rows = approve(
        root,
        cycle=args.cycle,
        proposal_sha256=args.proposal_sha256,
        reviewer=args.reviewer,
        confirmation=args.confirm,
        approved_at=args.approved_at,
    )
    output = root / mapping_study_paths(args.cycle).adjudications
    write_jsonl(rows, output)
    print(
        json.dumps(
            {
                "cycle": args.cycle,
                "record_count": len(rows),
                "proposal_sha256": args.proposal_sha256,
                "output": output.relative_to(root).as_posix(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

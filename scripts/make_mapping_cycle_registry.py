"""Generate evidence-derived lifecycle state for immutable mapping-study cycles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.io import write_jsonl
from reimburse_atlas.mapping_study_paths import (
    available_mapping_study_cycles,
    latest_mapping_study_cycle,
    mapping_study_paths,
)
from reimburse_atlas.registry import project_root

OUTPUT = Path("data/derived/mapping_study/cycle_registry.json")
ROWS = Path("data/derived/mapping_study/cycle_registry.jsonl")


def _json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return cast("dict[str, Any]", json.loads(path.read_text(encoding="utf-8")))


def build_registry(root: Path) -> dict[str, Any]:
    """Return lifecycle records inferred only from immutable cycle artifacts."""
    active = latest_mapping_study_cycle(root)
    records: list[dict[str, Any]] = []
    for cycle in available_mapping_study_cycles(root):
        paths = mapping_study_paths(cycle)
        frame = root / paths.frame
        summary = _json(root / paths.derived / "candidate_frame_summary.json")
        reviews = _json(root / paths.blind_review_summary)
        owner = _json(root / paths.owner_packet)
        split = _json(root / paths.split_plan)
        evaluation = _json(root / paths.evaluation)
        if evaluation.get("evaluated_once") is True:
            status = (
                "evaluated_accepted"
                if evaluation.get("status") == "accepted"
                else "evaluated_rejected"
            )
        elif split.get("status") == "ready":
            status = "split_ready"
        elif owner:
            status = (
                "adjudication_ready_for_owner"
                if owner.get("status") == "ready_for_owner_approval"
                else "spectrum_blocked"
            )
        elif reviews.get("independent_roles_complete") is True:
            status = "awaiting_adjudication"
        elif cycle == active:
            status = "active_review"
        else:
            status = "superseded_before_review"
        records.append({
            "cycle": cycle,
            "status": status,
            "active": cycle == active,
            "candidate_frame_sha256": hashlib.sha256(frame.read_bytes()).hexdigest(),
            "candidate_count": summary.get("candidate_count", 0),
            "effective_unique_groups": summary.get("effective_unique_groups"),
            "reviewer_case_count": reviews.get("reviewer_case_count", 0),
            "proposal_sha256": owner.get("proposal_sha256"),
            "quota_gap": owner.get("total_quota_gap"),
            "holdout_evaluated_once": evaluation.get("evaluated_once", False),
        })
    return {
        "schema_version": "mapping-study-cycle-registry-v1",
        "active_cycle": active,
        "cycle_count": len(records),
        "records": records,
    }


def main() -> None:
    """Write mapping cycle lifecycle evidence."""
    root = project_root()
    registry = build_registry(root)
    output = root / OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_jsonl(cast("list[dict[str, Any]]", registry["records"]), root / ROWS)
    print(
        json.dumps(
            {
                "active_cycle": registry["active_cycle"],
                "cycle_count": registry["cycle_count"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

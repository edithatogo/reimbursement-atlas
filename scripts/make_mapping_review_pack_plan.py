"""Build a deterministic, fail-closed plan for the mapping review pack."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from reimburse_atlas.registry import project_root

INPUT = Path("data/derived/vertical_slice/mapping_evidence_matrix.jsonl")
OUTPUT = Path("data/derived/vertical_slice/mapping_review_pack_plan.json")
SEED = "reimbursement-atlas-mapping-review-pack-v1"


def _rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _case_key(row: dict[str, Any]) -> str:
    values = (
        row.get("left_source_id", ""),
        row.get("left_code", ""),
        row.get("right_source_id", ""),
        row.get("right_code", ""),
    )
    return "|".join(str(value) for value in values)


def build_plan(root: Path | None = None) -> dict[str, Any]:
    """Return a reproducible pack plan without fabricating review cases."""
    repo = root or project_root()
    input_path = repo / INPUT
    rows = _rows(input_path) if input_path.exists() else []
    unique = {_case_key(row): row for row in rows}
    ordered_keys = sorted(
        unique, key=lambda key: hashlib.sha256(f"{SEED}|{key}".encode()).hexdigest()
    )
    development_target = 600
    holdout_target = 150
    available = len(ordered_keys)
    source_strata = Counter(
        f"{unique[key].get('left_source_id')}->{unique[key].get('right_source_id')}"
        for key in ordered_keys
    )
    return {
        "schema_version": "mapping-review-pack-plan-v1",
        "status": "ready"
        if available >= development_target + holdout_target
        else "blocked_source_cases",
        "input": str(INPUT),
        "input_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest()
        if input_path.exists()
        else None,
        "randomisation": {"algorithm": "sha256-sort", "seed": SEED},
        "targets": {
            "development_total": development_target,
            "development_positive": 300,
            "development_negative": 300,
            "holdout_total": holdout_target,
            "holdout_positive": 75,
            "holdout_negative": 75,
            "total": development_target + holdout_target,
        },
        "available_unique_candidates": available,
        "target_case_gap": max(development_target + holdout_target - available, 0),
        "source_strata_available": dict(sorted(source_strata.items())),
        "development_case_ids": ordered_keys[:development_target]
        if available >= development_target + holdout_target
        else [],
        "holdout_case_ids": ordered_keys[development_target : development_target + holdout_target]
        if available >= development_target + holdout_target
        else [],
        "review_boundary": {
            "case_text": "not stored by this planner; use rights-cleared local source records",
            "review_records": "not present; blinded dual review and adjudication remain pending",
            "holdout_frozen": False,
            "evidence_ready": False,
        },
    }


def main() -> None:
    """Write the deterministic mapping review-pack plan."""
    root = project_root()
    output = root / OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    plan = build_plan(root)
    output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: plan[key]
                for key in ("status", "available_unique_candidates", "target_case_gap")
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

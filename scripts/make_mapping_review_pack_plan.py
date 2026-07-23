"""Build a deterministic, adjudication-gated mapping review pack."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from reimburse_atlas.registry import project_root

INPUT = Path("data/derived/mapping_study/candidate_frame.jsonl")
ADJUDICATIONS = Path("data/mapping_study/adjudications.jsonl")
BLIND_REVIEWS = Path("data/mapping_study/blind_reviews.jsonl")
OUTPUT = Path("data/derived/vertical_slice/mapping_review_pack_plan.json")
SEED = "reimbursement-atlas-mapping-review-pack-v1"
FAMILY_QUOTAS = {
    "procedures_pathology": {"development": 120, "holdout": 30},
    "medicines": {"development": 80, "holdout": 20},
    "genomics_coverage": {"development": 60, "holdout": 15},
    "devices_other": {"development": 40, "holdout": 10},
}


def _rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _ordered(case_ids: list[str]) -> list[str]:
    return sorted(
        case_ids,
        key=lambda case_id: hashlib.sha256(f"{SEED}|{case_id}".encode()).hexdigest(),
    )


def build_plan(root: Path | None = None) -> dict[str, Any]:  # ruff:ignore[too-many-locals]
    """Return a reproducible split only after checksum-bound adjudication."""
    repo = root or project_root()
    input_path = repo / INPUT
    adjudication_path = repo / ADJUDICATIONS
    rows = _rows(input_path)
    unique = {str(row.get("case_id")): row for row in rows if row.get("case_id")}
    frame_sha256 = (
        hashlib.sha256(input_path.read_bytes()).hexdigest() if input_path.exists() else None
    )
    adjudications = {
        str(row.get("case_id")): row
        for row in _rows(adjudication_path)
        if row.get("candidate_frame_sha256") == frame_sha256
        and row.get("final_decision") in {"positive", "negative"}
    }
    review_pairs: dict[str, dict[str, dict[str, Any]]] = {}
    for review in _rows(repo / BLIND_REVIEWS):
        case_id = str(review.get("case_id", ""))
        role = str(review.get("reviewer_role", ""))
        if (
            case_id in unique
            and review.get("candidate_frame_sha256") == frame_sha256
            and role in {"reviewer_a", "reviewer_b"}
        ):
            review_pairs.setdefault(case_id, {})[role] = review
    independently_reviewed = {
        case_id
        for case_id, pair in review_pairs.items()
        if set(pair) == {"reviewer_a", "reviewer_b"}
    }
    admissible_adjudications = {
        case_id: decision
        for case_id, decision in adjudications.items()
        if case_id in independently_reviewed
        and decision.get("reviewer_a_decision")
        == review_pairs[case_id]["reviewer_a"].get("decision")
        and decision.get("reviewer_b_decision")
        == review_pairs[case_id]["reviewer_b"].get("decision")
    }

    development: list[str] = []
    holdout: list[str] = []
    quota_gaps: dict[str, dict[str, int]] = {}
    for family, quota in FAMILY_QUOTAS.items():
        quota_gaps[family] = {}
        for label in ("positive", "negative"):
            case_ids = _ordered([
                case_id
                for case_id, decision in admissible_adjudications.items()
                if case_id in unique
                and unique[case_id].get("family") == family
                and decision.get("final_decision") == label
            ])
            required = quota["development"] + quota["holdout"]
            quota_gaps[family][label] = max(0, required - len(case_ids))
            if len(case_ids) >= required:
                development.extend(case_ids[: quota["development"]])
                holdout.extend(case_ids[quota["development"] : required])

    ready = bool(unique) and not any(
        gap for family in quota_gaps.values() for gap in family.values()
    )
    available = len(unique)
    adjudicated = len(admissible_adjudications)
    source_strata = Counter(
        f"{row.get('left_source_id')}->{row.get('right_source_id')}" for row in unique.values()
    )
    return {
        "schema_version": "mapping-review-pack-plan-v2",
        "status": "ready"
        if ready
        else "blocked_adjudication"
        if available
        else "blocked_source_cases",
        "input": str(INPUT),
        "input_sha256": frame_sha256,
        "adjudications": str(ADJUDICATIONS),
        "blind_reviews": str(BLIND_REVIEWS),
        "independently_reviewed_count": len(independently_reviewed),
        "inadmissible_adjudication_count": len(adjudications) - adjudicated,
        "adjudication_count": adjudicated,
        "randomisation": {"algorithm": "sha256-sort", "seed": SEED},
        "targets": {
            "development_total": 600,
            "development_positive": 300,
            "development_negative": 300,
            "holdout_total": 150,
            "holdout_positive": 75,
            "holdout_negative": 75,
            "total": 750,
        },
        "available_unique_candidates": available,
        "target_case_gap": sum(gap for family in quota_gaps.values() for gap in family.values()),
        "family_label_gaps": quota_gaps,
        "source_strata_available": dict(sorted(source_strata.items())),
        "development_case_ids": sorted(development) if ready else [],
        "holdout_case_ids": sorted(holdout) if ready else [],
        "review_boundary": {
            "candidate_hypotheses_are_truth": False,
            "review_records": "two blinded reviews and accountable adjudication required",
            "split_assigned_after_reference_labels": ready,
            "holdout_frozen": ready,
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
                for key in (
                    "status",
                    "available_unique_candidates",
                    "adjudication_count",
                    "target_case_gap",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

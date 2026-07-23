"""Tune a transparent mapping threshold on development labels and freeze holdout predictions."""

from __future__ import annotations

import argparse
import hashlib
import json
from operator import itemgetter
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.crosswalk import jaccard_similarity, tokenise
from reimburse_atlas.io import write_jsonl
from reimburse_atlas.mapping_study_paths import DEFAULT_CYCLE, mapping_study_paths
from reimburse_atlas.registry import project_root


def _json(path: Path) -> dict[str, Any]:
    return cast("dict[str, Any]", json.loads(path.read_text(encoding="utf-8")))


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        cast("dict[str, Any]", json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _case_score(case: dict[str, Any]) -> float:
    left = cast("dict[str, Any]", case["left"])
    right = cast("dict[str, Any]", case["right"])
    left_text = " ".join(str(left.get(key, "")) for key in ("label", "description", "domain"))
    right_text = " ".join(str(right.get(key, "")) for key in ("label", "description", "domain"))
    return jaccard_similarity(set(tokenise(left_text)), set(tokenise(right_text)))


def _balanced_accuracy(
    case_ids: list[str], truth: dict[str, str], scores: dict[str, float], threshold: float
) -> float:
    positive = [case_id for case_id in case_ids if truth[case_id] == "positive"]
    negative = [case_id for case_id in case_ids if truth[case_id] == "negative"]
    sensitivity = sum(scores[case_id] >= threshold for case_id in positive) / len(positive)
    specificity = sum(scores[case_id] < threshold for case_id in negative) / len(negative)
    return (sensitivity + specificity) / 2


def build_threshold_predictions(  # ruff:ignore[too-many-locals]
    root: Path, cycle: str = DEFAULT_CYCLE
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return a development-tuned model and predictions without consulting holdout labels."""
    paths = mapping_study_paths(cycle)
    plan = _json(root / paths.split_plan)
    if plan.get("status") != "ready":
        message = "mapping split is not ready"
        raise ValueError(message)
    development = cast("list[str]", plan["development_case_ids"])
    holdout = cast("list[str]", plan["holdout_case_ids"])
    cases = {
        str(row["case_id"]): row for row in _jsonl(root / paths.packets / "reviewer_a_cases.jsonl")
    }
    adjudications = {
        str(row["case_id"]): str(row["final_decision"])
        for row in _jsonl(root / paths.adjudications)
        if row.get("case_id") in development
        and row.get("final_decision") in {"positive", "negative"}
    }
    if set(adjudications) != set(development):
        message = "development adjudications are incomplete"
        raise ValueError(message)
    if not set(development + holdout) <= set(cases):
        message = "split contains cases absent from the blinded evidence packet"
        raise ValueError(message)
    scores = {case_id: _case_score(cases[case_id]) for case_id in development + holdout}
    thresholds = sorted({0.0, 1.0, *(scores[case_id] for case_id in development)})
    ranked = [
        (
            _balanced_accuracy(development, adjudications, scores, threshold),
            threshold,
        )
        for threshold in thresholds
    ]
    best_accuracy, best_threshold = max(ranked, key=itemgetter(0, 1))
    development_fingerprint = hashlib.sha256("\n".join(sorted(development)).encode()).hexdigest()
    holdout_fingerprint = hashlib.sha256("\n".join(sorted(holdout)).encode()).hexdigest()
    model = {
        "schema_version": "mapping-development-threshold-v1",
        "study_cycle": cycle,
        "candidate_frame_sha256": plan["input_sha256"],
        "algorithm": "token_jaccard",
        "decision_rule": "positive_when_score_greater_than_or_equal_to_threshold",
        "threshold": best_threshold,
        "threshold_source": "development_only",
        "development_case_count": len(development),
        "development_fingerprint": development_fingerprint,
        "development_balanced_accuracy": best_accuracy,
        "holdout_case_count": len(holdout),
        "holdout_fingerprint": holdout_fingerprint,
        "holdout_labels_accessed_during_tuning": False,
    }
    predictions = [
        {
            "schema_version": "mapping-holdout-prediction-v1",
            "candidate_frame_sha256": plan["input_sha256"],
            "case_id": case_id,
            "score": scores[case_id],
            "threshold": best_threshold,
            "threshold_source": "development_only",
            "prediction": "positive" if scores[case_id] >= best_threshold else "negative",
        }
        for case_id in sorted(holdout)
    ]
    return model, predictions


def main() -> None:
    """Write the frozen development model and holdout predictions."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle", default=DEFAULT_CYCLE)
    args = parser.parse_args()
    root = project_root()
    paths = mapping_study_paths(args.cycle)
    model, predictions = build_threshold_predictions(root, args.cycle)
    model_path = root / paths.threshold_model
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text(json.dumps(model, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_jsonl(predictions, root / paths.holdout_predictions)
    print(
        json.dumps(
            {
                "threshold": model["threshold"],
                "development_balanced_accuracy": model["development_balanced_accuracy"],
                "holdout_predictions": len(predictions),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

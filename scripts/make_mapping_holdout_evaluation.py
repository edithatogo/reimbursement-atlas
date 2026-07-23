"""Evaluate a frozen mapping holdout once with exact binomial intervals."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root

PLAN = Path("data/derived/vertical_slice/mapping_review_pack_plan.json")
FRAME = Path("data/derived/mapping_study/candidate_frame.jsonl")
ADJUDICATIONS = Path("data/mapping_study/adjudications.jsonl")
PREDICTIONS = Path("data/mapping_study/holdout_predictions.jsonl")
OUTPUT = Path("data/derived/mapping_study/evaluation_summary.json")


def exact_interval(successes: int, total: int, alpha: float = 0.05) -> tuple[float, float]:
    """Return a two-sided Clopper-Pearson interval via binomial-tail inversion."""
    if total <= 0 or not 0 <= successes <= total:
        msg = "successes and total must satisfy 0 <= successes <= total and total > 0"
        raise ValueError(msg)
    lower = 0.0 if successes == 0 else _bisect_tail(successes, total, alpha / 2, upper=False)
    upper = 1.0 if successes == total else _bisect_tail(successes, total, alpha / 2, upper=True)
    return lower, upper


def _bisect_tail(successes: int, total: int, target: float, *, upper: bool) -> float:
    low, high = 0.0, 1.0
    for _ in range(80):
        probability = (low + high) / 2
        tail = (
            _binomial_cdf(successes, total, probability)
            if upper
            else 1 - _binomial_cdf(successes - 1, total, probability)
        )
        if (tail > target) is upper:
            low = probability
        else:
            high = probability
    return (low + high) / 2


def _binomial_cdf(maximum: int, total: int, probability: float) -> float:
    if maximum < 0:
        return 0.0
    if maximum >= total:
        return 1.0
    return sum(
        math.comb(total, count) * probability**count * (1 - probability) ** (total - count)
        for count in range(maximum + 1)
    )


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [
        cast("dict[str, Any]", json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_evaluation(root: Path) -> dict[str, Any]:
    """Build a fail-closed evaluation from exact frozen-holdout predictions."""
    plan_path = root / PLAN
    if not plan_path.is_file() or cast("dict[str, Any]", _read(plan_path)).get("status") != "ready":
        return _blocked("split_not_ready")
    plan = cast("dict[str, Any]", _read(plan_path))
    holdout = cast("list[str]", plan["holdout_case_ids"])
    fingerprint = hashlib.sha256("\n".join(sorted(holdout)).encode()).hexdigest()
    prior_path = root / OUTPUT
    if prior_path.is_file():
        prior = cast("dict[str, Any]", _read(prior_path))
        if prior.get("evaluated_once") is True and prior.get("holdout_fingerprint") != fingerprint:
            return _blocked("holdout_fingerprint_changed", fingerprint=fingerprint)
    predictions = {str(row.get("case_id")): row for row in _jsonl(root / PREDICTIONS)}
    if set(predictions) != set(holdout):
        return _blocked("holdout_predictions_incomplete", fingerprint=fingerprint)
    if any(row.get("threshold_source") != "development_only" for row in predictions.values()):
        return _blocked("threshold_not_development_only", fingerprint=fingerprint)
    frame = {str(row["case_id"]): row for row in _jsonl(root / FRAME)}
    truth = {
        str(row["case_id"]): row["final_decision"]
        for row in _jsonl(root / ADJUDICATIONS)
        if row.get("final_decision") in {"positive", "negative"}
    }
    grouped: dict[str, list[str]] = defaultdict(list)
    grouped["overall"] = holdout
    for case_id in holdout:
        grouped[str(frame[case_id]["family"])].append(case_id)
    metrics = {name: _metrics(case_ids, truth, predictions) for name, case_ids in grouped.items()}
    accepted = all(value["balanced_accuracy"]["estimate"] >= 0.7 for value in metrics.values())
    return {
        "schema_version": "mapping-evaluation-summary-v1",
        "status": "accepted" if accepted else "rejected",
        "candidate_frame_sha256": plan["input_sha256"],
        "holdout_fingerprint": fingerprint,
        "threshold_source": "development_only",
        "denominators": {name: len(case_ids) for name, case_ids in grouped.items()},
        "exclusions": {"count": 0, "reasons": []},
        "metrics": metrics,
        "evaluated_once": True,
    }


def _metrics(
    case_ids: list[str], truth: dict[str, str], predictions: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    tp = sum(
        truth.get(case_id) == "positive" and predictions[case_id]["prediction"] == "positive"
        for case_id in case_ids
    )
    tn = sum(
        truth.get(case_id) == "negative" and predictions[case_id]["prediction"] == "negative"
        for case_id in case_ids
    )
    fp = sum(
        truth.get(case_id) == "negative" and predictions[case_id]["prediction"] == "positive"
        for case_id in case_ids
    )
    fn = sum(
        truth.get(case_id) == "positive" and predictions[case_id]["prediction"] == "negative"
        for case_id in case_ids
    )
    sensitivity = _estimate(tp, tp + fn)
    specificity = _estimate(tn, tn + fp)
    return {
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        "sensitivity": sensitivity,
        "specificity": specificity,
        "precision": _estimate(tp, tp + fp),
        "negative_predictive_value": _estimate(tn, tn + fn),
        "balanced_accuracy": {
            "estimate": (sensitivity["estimate"] + specificity["estimate"]) / 2,
            "interval_method": "component_exact_intervals_reported_separately",
        },
    }


def _estimate(successes: int, total: int) -> dict[str, Any]:
    if total == 0:
        return {"estimate": 0.0, "lower_95": 0.0, "upper_95": 1.0, "n": 0}
    lower, upper = exact_interval(successes, total)
    return {
        "estimate": successes / total,
        "lower_95": lower,
        "upper_95": upper,
        "n": total,
    }


def _blocked(reason: str, *, fingerprint: str = "0" * 64) -> dict[str, Any]:
    return {
        "schema_version": "mapping-evaluation-summary-v1",
        "status": "blocked",
        "candidate_frame_sha256": "0" * 64,
        "holdout_fingerprint": fingerprint,
        "threshold_source": "development_only",
        "denominators": {},
        "exclusions": {"reason": reason},
        "metrics": {},
        "evaluated_once": False,
    }


def main() -> None:
    """Write the current holdout evaluation state."""
    root = project_root()
    result = build_evaluation(root)
    output = root / OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "exclusions": result["exclusions"]}, indent=2))


if __name__ == "__main__":
    main()

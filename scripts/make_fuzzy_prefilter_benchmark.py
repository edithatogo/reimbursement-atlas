"""Benchmark the Python fuzzy-prefilter against reviewed local fixture pairs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from reimburse_atlas.analysis.fuzzy_prefilter import fuzzy_prefilter
from reimburse_atlas.registry import project_root, repo_relative

FIXTURE_DIR = Path("data/derived/vertical_slice")
THRESHOLD = 0.2


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _label_index(root: Path) -> dict[tuple[str, str], str]:
    rows = _read_rows(root / FIXTURE_DIR / "schedule_items.csv")
    return {
        (row["source_id"], row["item_code"]): " ".join(
            value for value in (row["item_label"], row["item_description"]) if value
        )
        for row in rows
    }


def _score_pair(labels: dict[tuple[str, str], str], row: dict[str, str]) -> float:
    left_key = (row["left_source_id"], row["left_code"])
    right_key = (row["right_source_id"], row["right_code"])
    try:
        left_label = labels[left_key]
        right_label = labels[right_key]
    except KeyError as exc:
        missing_key = exc.args[0]
        message = f"Missing fixture label for {missing_key}"
        raise ValueError(message) from exc
    matches = fuzzy_prefilter(
        [left_label],
        [right_label],
        threshold=THRESHOLD,
        max_per_left=1,
    )
    return matches[0][2] if matches else 0.0


def build_benchmark(root: Path) -> dict[str, Any]:
    """Return deterministic recall and negative-control evidence."""
    labels = _label_index(root)
    gold = _read_rows(root / FIXTURE_DIR / "gold_standard_mappings.csv")
    negatives = _read_rows(root / FIXTURE_DIR / "negative_controls.csv")
    gold_scores = [_score_pair(labels, row) for row in gold]
    negative_scores = [_score_pair(labels, row) for row in negatives]
    true_positive = sum(score >= THRESHOLD for score in gold_scores)
    false_negative = len(gold_scores) - true_positive
    false_positive = sum(score >= THRESHOLD for score in negative_scores)
    true_negative = len(negative_scores) - false_positive
    recall = true_positive / len(gold_scores) if gold_scores else 0.0
    specificity = true_negative / len(negative_scores) if negative_scores else 0.0
    precision_denominator = true_positive + false_positive
    precision = true_positive / precision_denominator if precision_denominator else 0.0
    return {
        "schema_version": "fuzzy-prefilter-benchmark-v1",
        "status": "review_required",
        "python_reference_status": "pass",
        "publication_safe": True,
        "fixture_type": "synthetic_reviewed_pairs",
        "reviewer_signoff_required": True,
        "threshold": THRESHOLD,
        "gold_standard_count": len(gold),
        "negative_control_count": len(negatives),
        "true_positive_count": true_positive,
        "false_negative_count": false_negative,
        "false_positive_count": false_positive,
        "true_negative_count": true_negative,
        "recall": recall,
        "precision": precision,
        "specificity": specificity,
        "gold_standard_scores": [round(score, 6) for score in gold_scores],
        "negative_control_scores": [round(score, 6) for score in negative_scores],
        "notes": [
            "This is a candidate-generation prefilter, not an equivalence classifier.",
            "Synthetic fixture performance does not establish real-source recall.",
            "Human mapping adjudication is required before evidence-readiness claims.",
        ],
    }


def main() -> None:
    """Write the deterministic benchmark report."""
    root = project_root()
    report = build_benchmark(root)
    path = root / "data/derived/mojo/fuzzy_prefilter_benchmark.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {repo_relative(path)}")


if __name__ == "__main__":
    main()

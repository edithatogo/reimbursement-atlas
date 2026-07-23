from __future__ import annotations

import json
from pathlib import Path

from scripts.make_mapping_threshold_predictions import build_threshold_predictions


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _case(case_id: str, left: str, right: str) -> dict[str, object]:
    return {
        "case_id": case_id,
        "left": {"label": left, "description": left, "domain": "test"},
        "right": {"label": right, "description": right, "domain": "test"},
    }


def _fixture(root: Path, holdout_decisions: tuple[str, str], cycle: str = "initial") -> None:
    development = [f"map_{value:020x}" for value in range(4)]
    holdout = [f"map_{value:020x}" for value in range(4, 6)]
    plan = {
        "status": "ready",
        "input_sha256": "a" * 64,
        "development_case_ids": development,
        "holdout_case_ids": holdout,
    }
    if cycle == "initial":
        derived = root / "data/derived/mapping_study"
        review = root / "data/mapping_study"
        path = root / "data/derived/vertical_slice/mapping_review_pack_plan.json"
    else:
        derived = root / "data/derived/mapping_study" / cycle
        review = root / "data/mapping_study" / cycle
        path = derived / "mapping_review_pack_plan.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan), encoding="utf-8")
    _write_jsonl(
        derived / "blind_review_packets/reviewer_a_cases.jsonl",
        [
            _case(development[0], "same procedure", "same procedure"),
            _case(development[1], "same medicine", "same medicine"),
            _case(development[2], "alpha procedure", "unrelated device"),
            _case(development[3], "beta medicine", "different phenotype"),
            _case(holdout[0], "matching test", "matching test"),
            _case(holdout[1], "first concept", "second concept"),
        ],
    )
    _write_jsonl(
        review / "adjudications.jsonl",
        [
            *[
                {"case_id": case_id, "final_decision": decision}
                for case_id, decision in zip(
                    development,
                    ("positive", "positive", "negative", "negative"),
                    strict=True,
                )
            ],
            *[
                {"case_id": case_id, "final_decision": decision}
                for case_id, decision in zip(holdout, holdout_decisions, strict=True)
            ],
        ],
    )


def test_threshold_uses_development_labels_and_predicts_every_holdout_case(
    tmp_path: Path,
) -> None:
    _fixture(tmp_path, ("positive", "negative"))

    model, predictions = build_threshold_predictions(tmp_path)

    assert model["threshold_source"] == "development_only"
    assert model["holdout_labels_accessed_during_tuning"] is False
    assert model["development_balanced_accuracy"] == 1.0
    assert len(predictions) == 2
    assert {row["prediction"] for row in predictions} == {"positive", "negative"}


def test_holdout_truth_cannot_change_tuned_threshold(tmp_path: Path) -> None:
    _fixture(tmp_path, ("positive", "negative"))
    first_model, first_predictions = build_threshold_predictions(tmp_path)
    _fixture(tmp_path, ("negative", "positive"))

    second_model, second_predictions = build_threshold_predictions(tmp_path)

    assert first_model == second_model
    assert first_predictions == second_predictions


def test_threshold_outputs_are_bound_to_named_cycle(tmp_path: Path) -> None:
    _fixture(tmp_path, ("positive", "negative"), "expansion_v2")

    model, predictions = build_threshold_predictions(tmp_path, "expansion_v2")

    assert model["study_cycle"] == "expansion_v2"
    assert len(predictions) == 2

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.make_mapping_holdout_evaluation import build_evaluation, exact_interval


def test_exact_interval_matches_known_extreme_examples() -> None:
    assert exact_interval(0, 10)[1] == pytest.approx(0.308497, abs=1e-6)
    assert exact_interval(10, 10)[0] == pytest.approx(0.691503, abs=1e-6)


def test_evaluation_fails_closed_before_split(tmp_path: Path) -> None:
    result = build_evaluation(tmp_path)

    assert result["status"] == "blocked"
    assert result["exclusions"]["reason"] == "split_not_ready"
    assert result["evaluated_once"] is False


def test_evaluation_refuses_second_use_of_sealed_holdout(tmp_path: Path) -> None:
    cycle = "expansion_v9"
    derived = tmp_path / "data/derived/mapping_study" / cycle
    review = tmp_path / "data/mapping_study" / cycle
    derived.mkdir(parents=True)
    review.mkdir(parents=True)
    case_ids = ["map_" + "a" * 20, "map_" + "b" * 20]
    (derived / "mapping_review_pack_plan.json").write_text(
        json.dumps({
            "status": "ready",
            "input_sha256": "c" * 64,
            "holdout_case_ids": case_ids,
        }),
        encoding="utf-8",
    )
    (derived / "candidate_frame.jsonl").write_text(
        "\n".join(json.dumps({"case_id": case_id, "family": "medicines"}) for case_id in case_ids)
        + "\n",
        encoding="utf-8",
    )
    (review / "adjudications.jsonl").write_text(
        "\n".join(
            json.dumps({"case_id": case_id, "final_decision": decision})
            for case_id, decision in zip(case_ids, ("positive", "negative"), strict=True)
        )
        + "\n",
        encoding="utf-8",
    )
    (derived / "development_threshold.json").write_text("{}", encoding="utf-8")
    (review / "holdout_predictions.jsonl").write_text(
        "\n".join(
            json.dumps({
                "case_id": case_id,
                "prediction": decision,
                "threshold_source": "development_only",
            })
            for case_id, decision in zip(case_ids, ("positive", "negative"), strict=True)
        )
        + "\n",
        encoding="utf-8",
    )
    first = build_evaluation(tmp_path, cycle)
    (derived / "evaluation_summary.json").write_text(json.dumps(first), encoding="utf-8")

    second = build_evaluation(tmp_path, cycle)

    assert first["status"] == "accepted"
    assert second["status"] == "blocked"
    assert second["exclusions"]["reason"] == "holdout_evaluation_already_sealed"

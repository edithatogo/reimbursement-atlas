from __future__ import annotations

import json
from pathlib import Path

from scripts.make_mapping_review_pack_plan import build_plan


def test_pack_plan_fails_closed_without_enough_candidates(tmp_path: Path) -> None:
    input_path = tmp_path / "data/derived/vertical_slice/mapping_evidence_matrix.jsonl"
    input_path.parent.mkdir(parents=True)
    input_path.write_text(
        json.dumps({
            "left_source_id": "a",
            "left_code": "1",
            "right_source_id": "b",
            "right_code": "2",
        })
        + "\n"
    )

    plan = build_plan(tmp_path)

    assert plan["status"] == "blocked_source_cases"
    assert plan["available_unique_candidates"] == 1
    assert plan["target_case_gap"] == 749
    assert plan["development_case_ids"] == []
    assert plan["review_boundary"]["holdout_frozen"] is False


def test_pack_plan_is_deterministic_and_keeps_holdout_separate(tmp_path: Path) -> None:
    input_path = tmp_path / "data/derived/vertical_slice/mapping_evidence_matrix.jsonl"
    input_path.parent.mkdir(parents=True)
    rows = [
        {"left_source_id": "a", "left_code": str(i), "right_source_id": "b", "right_code": str(i)}
        for i in range(750)
    ]
    input_path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")

    first = build_plan(tmp_path)
    second = build_plan(tmp_path)

    assert first == second
    assert first["status"] == "ready"
    assert len(first["development_case_ids"]) == 600
    assert len(first["holdout_case_ids"]) == 150
    assert set(first["development_case_ids"]).isdisjoint(first["holdout_case_ids"])

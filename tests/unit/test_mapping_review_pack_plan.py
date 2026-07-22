from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.make_mapping_review_pack_plan import FAMILY_QUOTAS, build_plan


def _write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )


def test_pack_plan_fails_closed_without_real_candidates(tmp_path: Path) -> None:
    plan = build_plan(tmp_path)

    assert plan["status"] == "blocked_source_cases"
    assert plan["available_unique_candidates"] == 0
    assert plan["target_case_gap"] == 750
    assert plan["development_case_ids"] == []
    assert plan["review_boundary"]["holdout_frozen"] is False


def test_pack_plan_requires_adjudication_before_split(tmp_path: Path) -> None:
    frame_path = tmp_path / "data/derived/mapping_study/candidate_frame.jsonl"
    _write_rows(frame_path, [{"case_id": "map_" + "a" * 20, "family": "procedures_pathology"}])

    plan = build_plan(tmp_path)

    assert plan["status"] == "blocked_adjudication"
    assert plan["available_unique_candidates"] == 1
    assert plan["adjudication_count"] == 0
    assert plan["development_case_ids"] == []


def test_pack_plan_is_deterministic_balanced_and_disjoint(tmp_path: Path) -> None:
    frame_path = tmp_path / "data/derived/mapping_study/candidate_frame.jsonl"
    adjudication_path = tmp_path / "data/mapping_study/adjudications.jsonl"
    frame: list[dict[str, object]] = []
    decisions: list[dict[str, object]] = []
    index = 0
    for family, quotas in FAMILY_QUOTAS.items():
        for label in ("positive", "negative"):
            for _ in range(quotas["development"] + quotas["holdout"]):
                case_id = f"map_{index:020x}"
                frame.append({"case_id": case_id, "family": family})
                decisions.append({"case_id": case_id, "final_decision": label})
                index += 1
    _write_rows(frame_path, frame)
    frame_sha256 = hashlib.sha256(frame_path.read_bytes()).hexdigest()
    for decision in decisions:
        decision["candidate_frame_sha256"] = frame_sha256
    _write_rows(adjudication_path, decisions)

    first = build_plan(tmp_path)
    second = build_plan(tmp_path)

    assert first == second
    assert first["status"] == "ready"
    assert len(first["development_case_ids"]) == 600
    assert len(first["holdout_case_ids"]) == 150
    assert set(first["development_case_ids"]).isdisjoint(first["holdout_case_ids"])
    assert first["review_boundary"]["holdout_frozen"] is True

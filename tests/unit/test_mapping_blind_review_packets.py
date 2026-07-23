from __future__ import annotations

import json
from pathlib import Path

from scripts.make_mapping_blind_review_packets import build_packets, is_sealed_cycle


def test_current_blind_packets_are_complete_and_hide_hypotheses() -> None:
    cases, manifest = build_packets(Path.cwd())

    assert manifest["status"] == "ready"
    assert len(cases) == 1500
    assert all("proposed_label_hypothesis" not in case for case in cases)
    assert all("split" not in case for case in cases)


def test_expansion_cycle_uses_its_own_frozen_frame() -> None:
    cases, manifest = build_packets(Path.cwd(), "expansion_v2")

    assert manifest["status"] == "ready"
    assert manifest["study_cycle"] == "expansion_v2"
    assert manifest["candidate_frame_sha256"] == (
        "29b357cb20ee2328bb995e733b71075f549703a46f0b62e8a31c0a052a25916c"
    )
    assert len(cases) == 1500


def test_codebook_cycle_exposes_relation_but_not_hypothesis() -> None:
    cases, manifest = build_packets(Path.cwd(), "expansion_v4")

    assert manifest["status"] == "ready"
    assert all(case["schema_version"] == "mapping-blind-review-case-v2" for case in cases)
    assert all(case["target_relation"] for case in cases)
    assert all("billing-code equivalence" in case["decision_question"] for case in cases)
    assert all("candidate_score" not in case for case in cases)


def test_sealed_cycle_is_not_eligible_for_packet_regeneration(tmp_path: Path) -> None:
    evaluation = tmp_path / "data/derived/mapping_study/expansion_v9/evaluation_summary.json"
    evaluation.parent.mkdir(parents=True)
    evaluation.write_text(
        json.dumps({"evaluated_once": True}),
        encoding="utf-8",
    )

    assert is_sealed_cycle(tmp_path, "expansion_v9") is True
    assert is_sealed_cycle(tmp_path, "expansion_v8") is False

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.make_mapping_adjudication_packet import build_packet


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _fixture(root: Path) -> None:
    case_id = "map_" + "1" * 20
    frame_path = root / "data/derived/mapping_study/candidate_frame.jsonl"
    _write(
        frame_path,
        [{"case_id": case_id, "family": "medicines"}],
    )
    frame_sha = __import__("hashlib").sha256(frame_path.read_bytes()).hexdigest()
    _write(
        root / "data/mapping_study/blind_reviews.jsonl",
        [
            {"case_id": case_id, "reviewer_role": "reviewer_a", "decision": "positive"},
            {"case_id": case_id, "reviewer_role": "reviewer_b", "decision": "negative"},
        ],
    )
    _write(
        root / "data/mapping_study/adjudication_proposals.jsonl",
        [
            {
                "case_id": case_id,
                "candidate_frame_sha256": frame_sha,
                "reviewer_a_decision": "positive",
                "reviewer_b_decision": "negative",
                "final_decision": "positive",
            }
        ],
    )


def test_owner_packet_reports_candidate_spectrum_gap(tmp_path: Path) -> None:
    _fixture(tmp_path)

    packet = build_packet(tmp_path)

    assert packet["status"] == "blocked_candidate_spectrum"
    assert packet["proposal_count"] == 1
    assert packet["family_decision_counts"]["medicines"]["positive"] == 1
    assert packet["family_label_quota_gaps"]["medicines"]["positive"] == 99
    assert packet["accountable_owner_approval_required"] is True


def test_owner_packet_rejects_review_decision_drift(tmp_path: Path) -> None:
    _fixture(tmp_path)
    path = tmp_path / "data/mapping_study/adjudication_proposals.jsonl"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["reviewer_a_decision"] = "negative"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="blind ledger"):
        build_packet(tmp_path)

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.make_mapping_blind_review_ledger import build_ledger


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _row(case_id: str, role: str, decision: str) -> dict[str, object]:
    return {
        "candidate_frame_sha256": "a" * 64,
        "case_id": case_id,
        "reviewer_role": role,
        "decision": decision,
    }


def _fixture(root: Path) -> None:
    manifest = root / "data/derived/mapping_study/blind_review_packets/manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        json.dumps({"candidate_frame_sha256": "a" * 64, "case_count": 2}),
        encoding="utf-8",
    )
    cases = ["map_" + "1" * 20, "map_" + "2" * 20]
    _write(
        root / "data/mapping_study/reviewer_a_reviews.jsonl",
        [_row(cases[0], "reviewer_a", "positive"), _row(cases[1], "reviewer_a", "negative")],
    )
    _write(
        root / "data/mapping_study/reviewer_b_reviews.jsonl",
        [_row(cases[0], "reviewer_b", "positive"), _row(cases[1], "reviewer_b", "uncertain")],
    )


def _add_v2_receipts(root: Path) -> None:
    packet_root = root / "data/derived/mapping_study/blind_review_packets"
    packet = packet_root / "reviewer_a_cases.jsonl"
    _write(
        packet,
        [
            {"case_id": "map_" + "1" * 20},
            {"case_id": "map_" + "2" * 20},
        ],
    )
    packet_hash = hashlib.sha256(packet.read_bytes()).hexdigest()
    (packet_root / "reviewer_b_cases.jsonl").write_bytes(packet.read_bytes())
    manifest = {
        "schema_version": "mapping-blind-review-packet-manifest-v2",
        "candidate_frame_sha256": "a" * 64,
        "case_count": 2,
        "private_packet_sha256": packet_hash,
        "role_packet_sha256": {"reviewer_a": packet_hash, "reviewer_b": packet_hash},
    }
    (packet_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    for role in ("reviewer_a", "reviewer_b"):
        receipt = {
            "schema_version": "mapping-reviewer-session-receipt-v1",
            "reviewer_role": role,
            "reviewer_session_id": f"isolated-session-{role}",
            "bounded_mandate": "Independently classify only the supplied blinded mapping cases.",
            "candidate_frame_sha256": "a" * 64,
            "packet_sha256": packet_hash,
            "started_at": "2026-07-23T00:00:00Z",
            "completed_at": "2026-07-23T01:00:00Z",
            "isolation_attestation": {
                "other_review_not_accessed": True,
                "hypotheses_not_accessed": True,
                "split_assignment_not_accessed": True,
            },
        }
        path = root / f"data/mapping_study/{role}_receipt.json"
        path.write_text(json.dumps(receipt), encoding="utf-8")


def test_build_ledger_requires_complete_isolated_roles(tmp_path: Path) -> None:
    _fixture(tmp_path)

    ledger, summary = build_ledger(tmp_path)

    assert len(ledger) == 4
    assert summary["agreement_count"] == 1
    assert summary["disagreement_count"] == 1
    assert summary["percent_agreement"] == 0.5
    assert summary["cohen_kappa"] == pytest.approx(1 / 3)
    assert summary["accountable_adjudication_complete"] is False


def test_build_ledger_rejects_role_metadata_drift(tmp_path: Path) -> None:
    _fixture(tmp_path)
    path = tmp_path / "data/mapping_study/reviewer_b_reviews.jsonl"
    path.write_text(
        path.read_text(encoding="utf-8").replace('"reviewer_b"', '"reviewer_a"'),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="metadata"):
        build_ledger(tmp_path)


def test_build_ledger_rejects_v2_target_relation_drift(tmp_path: Path) -> None:
    _fixture(tmp_path)
    packet = tmp_path / ("data/derived/mapping_study/blind_review_packets/reviewer_a_cases.jsonl")
    cases = ["map_" + "1" * 20, "map_" + "2" * 20]
    _write(
        packet,
        [
            {
                "schema_version": "mapping-blind-review-case-v2",
                "case_id": case_id,
                "target_relation": "same_device_class_or_intended_use",
            }
            for case_id in cases
        ],
    )
    for role in ("reviewer_a", "reviewer_b"):
        path = tmp_path / f"data/mapping_study/{role}_reviews.jsonl"
        rows = [
            {
                **json.loads(line),
                "target_relation": "same_active_ingredient_or_therapeutic_moiety",
            }
            for line in path.read_text(encoding="utf-8").splitlines()
        ]
        _write(path, rows)

    with pytest.raises(ValueError, match="target relation"):
        build_ledger(tmp_path)


def test_v2_manifest_requires_distinct_isolated_review_receipts(tmp_path: Path) -> None:
    _fixture(tmp_path)
    _add_v2_receipts(tmp_path)
    receipt = tmp_path / "data/mapping_study/reviewer_b_receipt.json"
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    payload["reviewer_session_id"] = "isolated-session-reviewer_a"
    receipt.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="distinct session"):
        build_ledger(tmp_path)

from __future__ import annotations

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


def test_build_ledger_requires_complete_isolated_roles(tmp_path: Path) -> None:
    _fixture(tmp_path)

    ledger, summary = build_ledger(tmp_path)

    assert len(ledger) == 4
    assert summary["agreement_count"] == 1
    assert summary["disagreement_count"] == 1
    assert summary["percent_agreement"] == 0.5
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

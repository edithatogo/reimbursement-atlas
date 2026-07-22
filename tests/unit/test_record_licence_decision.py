"""Tests for the safe checksum-bound decision recorder."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.record_licence_decision import record_decision


def _fixture_repo(tmp_path: Path) -> tuple[Path, str]:
    candidate = tmp_path / "data/derived/example.csv"
    candidate.parent.mkdir(parents=True)
    candidate.write_text("value\n", encoding="utf-8")
    import hashlib

    checksum = hashlib.sha256(candidate.read_bytes()).hexdigest()
    queue = tmp_path / "data/derived/licence_review/licence_review_queue.jsonl"
    queue.parent.mkdir(parents=True)
    queue.write_text(
        json.dumps({
            "review_id": "review_example",
            "relative_path": "data/derived/example.csv",
            "checksum_sha256": checksum,
            "review_status": "pending",
            "reviewer": "",
            "reviewed_at": "",
        })
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "data/licence_review").mkdir(parents=True)
    return tmp_path, checksum


def _decision(checksum: str) -> dict[str, str]:
    return {
        "review_id": "review_example",
        "relative_path": "data/derived/example.csv",
        "checksum_sha256": checksum,
        "decision": "blocked",
        "reviewer": "repository-owner",
        "reviewed_at": "2026-07-22",
        "source_terms": "Terms recorded in the review matrix.",
        "attribution": "Retain source attribution.",
        "redistribution_permission": "Not approved.",
        "restrictions": "No raw payloads.",
        "evidence": "Reviewed exact candidate checksum.",
    }


def test_record_decision_validates_checksum_and_appends(tmp_path: Path) -> None:
    root, checksum = _fixture_repo(tmp_path)
    decision_file = tmp_path / "decision.json"
    decision_file.write_text(json.dumps(_decision(checksum)), encoding="utf-8")

    record_decision(decision_file, root=root)

    rows = (root / "data/licence_review/decisions.jsonl").read_text(encoding="utf-8")
    assert json.loads(rows)["checksum_sha256"] == checksum


def test_record_decision_rejects_stale_checksum_without_write(tmp_path: Path) -> None:
    root, _ = _fixture_repo(tmp_path)
    decision_file = tmp_path / "decision.json"
    decision_file.write_text(json.dumps(_decision("0" * 64)), encoding="utf-8")

    with pytest.raises(ValueError, match="checksum"):
        record_decision(decision_file, root=root)

    assert not (root / "data/licence_review/decisions.jsonl").exists()

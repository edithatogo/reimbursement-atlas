from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.approve_mapping_adjudication import approve


def _fixture(root: Path) -> str:
    path = root / "data/mapping_study/expansion_v7/adjudication_proposals.jsonl"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps({
            "case_id": "map_" + "a" * 20,
            "accountable_reviewer": "proposal-not-owner",
            "final_decision": "positive",
        })
        + "\n",
        encoding="utf-8",
    )
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_approval_is_bound_to_exact_proposal_checksum(tmp_path: Path) -> None:
    digest = _fixture(tmp_path)

    rows = approve(
        tmp_path,
        cycle="expansion_v7",
        proposal_sha256=digest,
        reviewer="Accountable Owner",
        confirmation=f"APPROVE_MAPPING_ADJUDICATION:{digest}",
        approved_at="2026-07-23T08:00:00+10:00",
    )

    assert rows[0]["accountable_reviewer"] == "Accountable Owner"
    assert rows[0]["approved_proposal_sha256"] == digest
    assert rows[0]["accountable_approved_at"] == "2026-07-22T22:00:00Z"


def test_approval_rejects_generic_confirmation(tmp_path: Path) -> None:
    digest = _fixture(tmp_path)

    with pytest.raises(ValueError, match="checksum-bound"):
        approve(
            tmp_path,
            cycle="expansion_v7",
            proposal_sha256=digest,
            reviewer="Accountable Owner",
            confirmation="APPROVE",
            approved_at="2026-07-23T08:00:00Z",
        )

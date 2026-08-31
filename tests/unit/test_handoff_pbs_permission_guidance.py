"""Handoff guidance must reflect permission, not repeatedly request it."""

import json
from pathlib import Path

import pytest

from reimburse_atlas.final_handoff import build_final_handoff_tasks

ROOT = Path(__file__).resolve().parents[2]
PERMISSION = "data/licence_review/pbs_raw_permission.json"


def test_active_permission_removes_repeated_handoff_approval(tmp_path: Path) -> None:
    target = tmp_path / PERMISSION
    target.parent.mkdir(parents=True)
    target.write_bytes((ROOT / PERMISSION).read_bytes())
    tasks = {task.id: task for task in build_final_handoff_tasks(tmp_path)}
    task = tasks["final_historical_source_expansion"]
    assert "no repeated approval" in task.required_environment
    assert "owner-attested" in task.recommended_action
    assert "written permission" not in task.unblock_condition
    assert "December 1987" in task.unblock_condition
    assert "permission does not prove acquisition or publication" in task.unblock_condition
    assert task.status == "partial"
    assert task.review_record == PERMISSION
    assert PERMISSION in task.gate_evidence
    dashboard = tasks["final_dashboard_visual_review"]
    assert "test-count contract" in dashboard.recommended_action
    assert "64-test" not in dashboard.recommended_action


@pytest.mark.parametrize("condition", ["missing", "revoked", "malformed"])
def test_invalid_permission_keeps_raw_boundary(tmp_path: Path, condition: str) -> None:
    if condition != "missing":
        target = tmp_path / PERMISSION
        target.parent.mkdir(parents=True)
        payload = json.loads((ROOT / PERMISSION).read_text())
        if condition == "revoked":
            payload["permission_status"] = "revoked"
        else:
            del payload["preservation_controls"]
        target.write_text(json.dumps(payload))
    task = next(
        row
        for row in build_final_handoff_tasks(tmp_path)
        if row.id == "final_historical_source_expansion"
    )
    assert "unavailable without a valid permission basis" in task.unblock_condition
    assert (
        "Publish only governed provenance and permitted derived fields" in task.recommended_action
    )
    assert "no repeated approval" not in task.required_environment
    assert task.review_record is None

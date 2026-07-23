from __future__ import annotations

import json
from pathlib import Path

from scripts.make_mapping_cycle_registry import build_registry


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload) + ("\n" if isinstance(payload, dict) else ""),
        encoding="utf-8",
    )


def test_registry_marks_latest_cycle_active_and_prior_unreviewed_cycle_superseded(
    tmp_path: Path,
) -> None:
    for cycle in ("expansion_v2", "expansion_v3"):
        directory = tmp_path / "data/derived/mapping_study" / cycle
        _write(directory / "candidate_frame.jsonl", {"case_id": cycle})
        _write(directory / "candidate_frame_summary.json", {"candidate_count": 1})

    registry = build_registry(tmp_path)

    assert registry["active_cycle"] == "expansion_v3"
    states = {row["cycle"]: row["status"] for row in registry["records"]}
    assert states["expansion_v2"] == "superseded_before_review"
    assert states["expansion_v3"] == "active_review"

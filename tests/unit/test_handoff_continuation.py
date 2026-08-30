"""Completed publication tasks dispatch verification, never another publication."""

import json
from pathlib import Path

import pytest

from reimburse_atlas.final_handoff import build_final_handoff_tasks


@pytest.mark.parametrize("tag", ["v0.1.1", "v1.0.0-rc.1", "v1.0.0; echo unsafe", None])
def test_zenodo_verification_uses_recorded_identity(tmp_path: Path, tag: str | None) -> None:
    path = tmp_path / "data/derived/zenodo/external_state.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps({
            "status": "published",
            "deposition_id": "21759294",
            "release_tag": tag,
        })
    )
    row = next(row for row in build_final_handoff_tasks(tmp_path) if row.id == "final_zenodo_draft")
    if tag in {"v0.1.1", "v1.0.0-rc.1"}:
        assert row.command == (
            "gh workflow run zenodo-preflight.yml -f mode=verify "
            f"-f deposition_id=21759294 -f release_tag={tag}"
        )
        assert "read-only" in row.recommended_action
    else:
        assert row.command.endswith("--help")
        assert "Recover the existing deposition ID" in row.recommended_action

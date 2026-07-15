"""Tests for non-depositing Zenodo metadata preparation."""

import json
from pathlib import Path

from scripts.validate_zenodo_metadata import validate_metadata


def test_repository_zenodo_metadata_is_valid() -> None:
    """The prepared metadata contains the required archival fields."""
    path = Path(__file__).parents[2] / ".zenodo.json"
    assert validate_metadata(path) == []


def test_zenodo_metadata_rejects_non_software_license(tmp_path: Path) -> None:
    """The validator rejects metadata that could misstate the software licence."""
    payload = json.loads((Path(__file__).parents[2] / ".zenodo.json").read_text())
    payload["license"] = "MIT"
    path = tmp_path / ".zenodo.json"
    path.write_text(json.dumps(payload))
    assert "software metadata must use Apache-2.0" in validate_metadata(path)

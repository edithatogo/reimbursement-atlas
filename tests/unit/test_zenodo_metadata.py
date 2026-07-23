"""Tests for non-depositing Zenodo metadata preparation."""

import json
from pathlib import Path

from scripts.make_zenodo_deposition_draft import build_draft
from scripts.validate_zenodo_metadata import validate_datacite_metadata, validate_metadata


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


def test_generated_datacite_metadata_is_valid() -> None:
    _, datacite, _ = build_draft(Path.cwd())

    assert validate_datacite_metadata(datacite) == []


def test_datacite_metadata_rejects_missing_coverage_and_bad_relationships() -> None:
    _, datacite, _ = build_draft(Path.cwd())
    datacite["dates"] = []
    datacite["geoLocations"] = []
    datacite["relatedIdentifiers"][0]["relationType"] = "MadeUpRelation"

    errors = validate_datacite_metadata(datacite)

    assert "DataCite dates must include temporal coverage with dateType Valid" in errors
    assert "DataCite geoLocations must identify geographic coverage" in errors
    assert "DataCite related identifier is incomplete or unsupported" in errors


def test_datacite_metadata_rejects_preflight_wording() -> None:
    _, datacite, _ = build_draft(Path.cwd())
    datacite["descriptions"][0]["description"] = "Preparation only; no Zenodo deposition."

    assert (
        "final DataCite descriptions must not contain preflight wording"
        in validate_datacite_metadata(datacite)
    )

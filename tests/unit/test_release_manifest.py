"""Tests for deterministic tagged-release metadata."""

import json
from pathlib import Path

import pytest

from scripts.make_release_manifest import build_manifest


def test_release_manifest_contains_sorted_checksum_subjects(tmp_path: Path, monkeypatch) -> None:
    """Manifest subjects are stable and checksum-bound."""
    monkeypatch.chdir(tmp_path)
    second = Path("b.txt")
    first = Path("a.txt")
    second.write_text("second", encoding="utf-8")
    first.write_text("first", encoding="utf-8")

    manifest = build_manifest("v1.2.3", "a" * 40, [second, first])

    assert [subject["path"] for subject in manifest["subjects"]] == ["a.txt", "b.txt"]
    assert manifest["zenodo_deposition"] == "disabled_pending_publication_approval"
    assert json.loads(json.dumps(manifest))["commit"] == "a" * 40


def test_release_manifest_rejects_invalid_tag_or_path(tmp_path: Path, monkeypatch) -> None:
    """Release metadata must not accept ambiguous tags or missing subjects."""
    monkeypatch.chdir(tmp_path)
    artifact = Path("artifact.whl")
    artifact.write_bytes(b"release")

    with pytest.raises(ValueError, match="version tag"):
        build_manifest("release", "a" * 40, [artifact])
    with pytest.raises(ValueError, match="does not exist"):
        build_manifest("v1.0.0", "a" * 40, [Path("missing")])

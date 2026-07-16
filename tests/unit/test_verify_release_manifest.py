"""Tests for offline release-manifest verification."""

import hashlib
import json
from pathlib import Path

import pytest

from scripts.make_release_manifest import build_manifest
from scripts.verify_release_manifest import verify_manifest


def test_verify_release_manifest_checks_subject_hashes(tmp_path: Path, monkeypatch) -> None:
    """A manifest verifies the expected tag, commit and local subjects."""
    monkeypatch.chdir(tmp_path)
    subject = Path("release.whl")
    subject.write_bytes(b"release")
    manifest = build_manifest("v1.2.3", "a" * 40, [Path("release.whl")])
    manifest_path = tmp_path / "release-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert (
        verify_manifest(
            manifest_path,
            tmp_path,
            expected_tag="v1.2.3",
            expected_commit="a" * 40,
        )
        == 1
    )


def test_verify_release_manifest_rejects_tampering(tmp_path: Path, monkeypatch) -> None:
    """A changed subject or unsafe path fails closed."""
    monkeypatch.chdir(tmp_path)
    subject = Path("release.whl")
    subject.write_bytes(b"release")
    manifest = build_manifest("v1.2.3", "a" * 40, [Path("release.whl")])
    manifest["subjects"][0]["sha256"] = hashlib.sha256(b"tampered").hexdigest()
    manifest_path = tmp_path / "release-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="checksum mismatch"):
        verify_manifest(manifest_path, tmp_path)

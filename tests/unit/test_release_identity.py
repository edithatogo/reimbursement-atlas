from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.validate_release_identity import validate_release_identity


def _root(tmp_path: Path, *, version: str = "1.2.3") -> Path:
    (tmp_path / "data/derived/zenodo").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nname = "reimburse-atlas"\nversion = "{version}"\n',
        encoding="utf-8",
    )
    (tmp_path / "CITATION.cff").write_text(
        f"cff-version: 1.2.0\nversion: {version}\ndate-released: 2026-07-23\n",
        encoding="utf-8",
    )
    for name in ("deposition_metadata.json", "datacite_metadata.json"):
        (tmp_path / "data/derived/zenodo" / name).write_text(
            json.dumps({"version": version}), encoding="utf-8"
        )
    return tmp_path


def test_release_identity_accepts_aligned_version_surfaces(tmp_path: Path) -> None:
    root = _root(tmp_path)
    asset = root / "reimburse_atlas-1.2.3-py3-none-any.whl"
    asset.touch()

    result = validate_release_identity(root, "v1.2.3", [asset])

    assert result["status"] == "pass"


def test_release_identity_rejects_tag_or_asset_drift(tmp_path: Path) -> None:
    root = _root(tmp_path)
    asset = root / "reimburse_atlas-2.0.0-py3-none-any.whl"
    asset.touch()

    with pytest.raises(ValueError, match=r"tag_version_mismatch.*asset_version_mismatch"):
        validate_release_identity(root, "v2.0.0", [asset])

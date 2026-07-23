"""Validate version identity across a tag, package, citation and registry drafts."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, cast

import yaml

from reimburse_atlas.registry import project_root


def validate_release_identity(root: Path, tag: str, assets: list[Path]) -> dict[str, object]:
    """Return a stable report or raise when release identity surfaces diverge."""
    project = cast(
        "dict[str, Any]",
        tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"],
    )
    version = str(project["version"])
    citation = cast(
        "dict[str, Any]",
        yaml.safe_load((root / "CITATION.cff").read_text(encoding="utf-8")),
    )
    zenodo = cast(
        "dict[str, Any]",
        json.loads(
            (root / "data/derived/zenodo/deposition_metadata.json").read_text(encoding="utf-8")
        ),
    )
    datacite = cast(
        "dict[str, Any]",
        json.loads(
            (root / "data/derived/zenodo/datacite_metadata.json").read_text(encoding="utf-8")
        ),
    )
    errors: list[str] = []
    if tag != f"v{version}":
        errors.append("tag_version_mismatch")
    if str(citation.get("version")) != version:
        errors.append("citation_version_mismatch")
    try:
        released = date.fromisoformat(str(citation.get("date-released")))
    except ValueError:
        errors.append("citation_release_date_invalid")
    else:
        if released > datetime.now(tz=UTC).date():
            errors.append("citation_release_date_future")
    if str(zenodo.get("version")) != version:
        errors.append("zenodo_version_mismatch")
    if str(datacite.get("version")) != version:
        errors.append("datacite_version_mismatch")
    normalised = version.replace("-", "_")
    for asset in assets:
        name = asset.name
        if (
            name.endswith((".whl", ".tar.gz"))
            and name.startswith(("reimburse_atlas-", "reimburse-atlas-"))
            and re.search(rf"[-_]{re.escape(normalised)}(?:[-.]|\.tar\.gz$)", name) is None
        ):
            errors.append(f"asset_version_mismatch:{name}")
    if errors:
        raise ValueError(",".join(errors))
    return {"status": "pass", "tag": tag, "version": version, "assets_checked": len(assets)}


def main() -> None:
    """Validate command-line release identity inputs."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--asset", action="append", type=Path, default=[])
    args = parser.parse_args()
    print(
        json.dumps(
            validate_release_identity(project_root(), args.tag, args.asset),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

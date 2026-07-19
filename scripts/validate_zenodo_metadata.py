"""Validate locally prepared Zenodo metadata without contacting Zenodo."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root, repo_relative

REQUIRED_KEYS = ("title", "upload_type", "description", "creators", "license")


def validate_metadata(path: Path) -> list[str]:  # ruff:ignore[too-many-branches]
    """Return validation errors for a local, non-depositing Zenodo record."""
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read valid JSON metadata: {exc}"]
    if not isinstance(payload, dict):
        return ["metadata must be a JSON object"]
    payload = cast("dict[str, Any]", payload)
    errors = [f"missing required key: {key}" for key in REQUIRED_KEYS if key not in payload]
    if payload.get("upload_type") != "software":
        errors.append("upload_type must be software")
    if payload.get("license") != "Apache-2.0":
        errors.append("software metadata must use Apache-2.0")
    creators = payload.get("creators")
    creator_errors = False
    if isinstance(creators, list):
        creator_errors = not creators
        for creator in cast("list[Any]", creators):
            if not isinstance(creator, dict) or not cast("dict[str, Any]", creator).get("name"):
                creator_errors = True
    else:
        creator_errors = True
    if creator_errors:
        errors.append("creators must contain at least one named creator")
    related = payload.get("related_identifiers", [])
    repository_identifier = False
    if isinstance(related, list):
        for item in cast("list[Any]", related):
            if isinstance(item, dict) and cast("dict[str, Any]", item).get("identifier") == (
                "https://github.com/edithatogo/reimbursement-atlas"
            ):
                repository_identifier = True
                break
    if not repository_identifier:
        errors.append("GitHub repository related identifier is required")
    return errors


def main() -> None:
    """Validate the repository's prepared metadata and never deposit it."""
    path = project_root() / ".zenodo.json"
    errors = validate_metadata(path)
    if errors:
        raise SystemExit("Zenodo metadata validation failed: " + "; ".join(errors))
    print(f"Zenodo metadata validation passed: {repo_relative(path)}")


if __name__ == "__main__":
    main()

"""Validate the repository's machine-readable citation metadata."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml

from reimburse_atlas.registry import project_root

REQUIRED_SCALARS = {
    "cff-version",
    "title",
    "message",
    "type",
    "version",
    "date-released",
    "license",
    "repository-code",
    "abstract",
}


def validate_citation(path: Path) -> list[str]:
    """Return validation errors for a CITATION.cff document."""
    try:
        payload: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [f"could not parse {path}: {exc}"]
    if not isinstance(payload, dict):
        return ["top-level citation document must be a mapping"]
    document = cast("dict[str, Any]", payload)
    errors = [f"missing required key: {key}" for key in sorted(REQUIRED_SCALARS - set(document))]
    if document.get("cff-version") != "1.2.0":
        errors.append("cff-version must be 1.2.0")
    if document.get("type") != "software":
        errors.append("type must be software")
    if document.get("license") != "Apache-2.0":
        errors.append("software license must be Apache-2.0")
    authors = document.get("authors")
    if not isinstance(authors, list) or not authors:
        errors.append("authors must contain at least one author")
    elif any(
        not isinstance(author, dict) or not cast("dict[str, Any]", author).get("family-names")
        for author in cast("list[Any]", authors)
    ):
        errors.append("each author must include family-names")
    repository = document.get("repository-code")
    if not isinstance(repository, str) or not repository.startswith("https://"):
        errors.append("repository-code must be an HTTPS URL")
    return errors


def main() -> None:
    """Validate CITATION.cff and exit non-zero on contract violations."""
    path = project_root() / "CITATION.cff"
    errors = validate_citation(path)
    if errors:
        raise SystemExit("Citation validation failed:\n- " + "\n- ".join(errors))
    print(f"Citation validation passed: {path}")


if __name__ == "__main__":
    main()

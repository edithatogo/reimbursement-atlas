"""Validate optional human-review decision files against committed JSON Schemas."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from reimburse_atlas.registry import project_root

REVIEW_CONTRACTS = (
    ("licence_review", "decision.schema.json", "decisions.jsonl"),
    ("mapping_review", "decision.schema.json", "decisions.jsonl"),
)


def validate_review_file(
    root: Path, review_dir: str, schema_name: str, decisions_name: str
) -> list[str]:
    """Return validation errors for one optional reviewer decision file."""
    schema_path = root / "data" / review_dir / schema_name
    decisions_path = root / "data" / review_dir / decisions_name
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"{schema_path}: cannot read schema: {error}"]

    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
    except SchemaError as error:  # pragma: no cover - defensive boundary for a committed schema
        return [f"{schema_path}: invalid JSON Schema: {error}"]

    if not decisions_path.exists():
        return []

    errors: list[str] = []
    for line_number, line in enumerate(decisions_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            instance: Any = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"{decisions_path}:{line_number}: invalid JSON: {error.msg}")
            continue
        for validation_error in cast("Any", validator).iter_errors(instance):
            location = ".".join(str(part) for part in validation_error.absolute_path) or "$"
            errors.append(f"{decisions_path}:{line_number}:{location}: {validation_error.message}")
    return errors


def main() -> None:
    """Exit non-zero when any optional human decision file violates its schema."""
    root = project_root()
    errors: list[str] = []
    counts: list[str] = []
    for review_dir, schema_name, decisions_name in REVIEW_CONTRACTS:
        errors.extend(validate_review_file(root, review_dir, schema_name, decisions_name))
        path = root / "data" / review_dir / decisions_name
        count = (
            sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
            if path.exists()
            else 0
        )
        counts.append(f"{review_dir}={count}")
    if errors:
        raise SystemExit("Review schema validation failed:\n- " + "\n- ".join(errors))
    print("Review schema validation passed: " + ", ".join(counts))


if __name__ == "__main__":
    main()

"""Validate optional human-review decision files against committed JSON Schemas."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from reimburse_atlas.registry import project_root

REVIEW_CONTRACTS = (
    ("licence_review", "decision.schema.json", "decisions.jsonl"),
    ("mapping_review", "decision.schema.json", "decisions.jsonl"),
    ("research_claims", "decision.schema.json", "decisions.jsonl"),
)
ROOT_JSONL_REVIEW_CONTRACTS = (
    (
        "mapping_study_blind_reviews",
        "schema/MappingBlindReviewRecord.schema.json",
        "data/mapping_study/blind_reviews.jsonl",
    ),
    (
        "mapping_study_adjudications",
        "schema/MappingAdjudicationRecord.schema.json",
        "data/mapping_study/adjudications.jsonl",
    ),
)
CYCLE_JSONL_REVIEW_CONTRACTS = (
    (
        "mapping_study_blind_reviews",
        "schema/MappingBlindReviewRecord.schema.json",
        "blind_reviews.jsonl",
    ),
    (
        "mapping_study_adjudications",
        "schema/MappingAdjudicationRecord.schema.json",
        "adjudications.jsonl",
    ),
)
CYCLE_JSON_REVIEW_CONTRACTS = (
    (
        "mapping_reviewer_a_receipt",
        "schema/MappingReviewerSessionReceipt.schema.json",
        "reviewer_a_receipt.json",
    ),
    (
        "mapping_reviewer_b_receipt",
        "schema/MappingReviewerSessionReceipt.schema.json",
        "reviewer_b_receipt.json",
    ),
)
JSON_REVIEW_CONTRACTS = (
    (
        "dashboard_review",
        "schema/DashboardHumanReviewRecord.schema.json",
        "data/derived/dashboard_review/human_review.json",
    ),
    (
        "osf_publication_review",
        "schema/OsfPublicationDecision.schema.json",
        "data/osf_review/publication_decision.json",
    ),
    (
        "osf_registration_review",
        "schema/OsfRegistrationDecision.schema.json",
        "data/osf_review/registration_decision.json",
    ),
)


def _is_date_time(value: object) -> bool:
    if not isinstance(value, str):
        return True
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False
    return "T" in value


def _format_checker() -> FormatChecker:
    checker = FormatChecker()
    if "date-time" not in checker.checkers:
        checker.checks("date-time")(_is_date_time)
    return checker


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
        validator = Draft202012Validator(schema, format_checker=_format_checker())
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


def validate_review_document(root: Path, schema_name: str, document_name: str) -> list[str]:
    """Return validation errors for one optional JSON review document."""
    schema_path = root / schema_name
    document_path = root / document_name
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"{schema_path}: cannot read schema: {error}"]
    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=_format_checker())
    except SchemaError as error:  # pragma: no cover - defensive boundary for a committed schema
        return [f"{schema_path}: invalid JSON Schema: {error}"]
    if not document_path.exists():
        return []
    try:
        instance: Any = json.loads(document_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"{document_path}: invalid JSON: {error}"]
    return [
        f"{document_path}:{'.'.join(str(part) for part in error.absolute_path) or '$'}: "
        f"{error.message}"
        for error in cast("Any", validator).iter_errors(instance)
    ]


def validate_root_jsonl_review(root: Path, schema_name: str, document_name: str) -> list[str]:
    """Validate an optional JSONL review file against a root-level schema."""
    schema_path = root / schema_name
    document_path = root / document_name
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=_format_checker())
    except (OSError, json.JSONDecodeError, SchemaError) as error:
        return [f"{schema_path}: cannot load valid schema: {error}"]
    if not document_path.exists():
        return []
    errors: list[str] = []
    for line_number, line in enumerate(document_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            instance: Any = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"{document_path}:{line_number}: invalid JSON: {error.msg}")
            continue
        for validation_error in cast("Any", validator).iter_errors(instance):
            location = ".".join(str(part) for part in validation_error.absolute_path) or "$"
            errors.append(f"{document_path}:{line_number}:{location}: {validation_error.message}")
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
    for review_dir, schema_name, document_name in JSON_REVIEW_CONTRACTS:
        errors.extend(validate_review_document(root, schema_name, document_name))
        counts.append(f"{review_dir}={'1' if (root / document_name).exists() else '0'}")
    for review_name, schema_name, document_name in ROOT_JSONL_REVIEW_CONTRACTS:
        errors.extend(validate_root_jsonl_review(root, schema_name, document_name))
        path = root / document_name
        count = (
            sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
            if path.exists()
            else 0
        )
        counts.append(f"{review_name}={count}")
    cycle_root = root / "data/mapping_study"
    for review_name, schema_name, filename in CYCLE_JSONL_REVIEW_CONTRACTS:
        for path in sorted(cycle_root.glob(f"*/{filename}")):
            relative = path.relative_to(root).as_posix()
            errors.extend(validate_root_jsonl_review(root, schema_name, relative))
            count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
            counts.append(f"{review_name}[{path.parent.name}]={count}")
    for review_name, schema_name, filename in CYCLE_JSON_REVIEW_CONTRACTS:
        for path in sorted(cycle_root.glob(f"*/{filename}")):
            relative = path.relative_to(root).as_posix()
            errors.extend(validate_review_document(root, schema_name, relative))
            counts.append(f"{review_name}[{path.parent.name}]=1")
    if errors:
        raise SystemExit("Review schema validation failed:\n- " + "\n- ".join(errors))
    print("Review schema validation passed: " + ", ".join(counts))


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.validate_review_schemas import validate_review_document


def _schema() -> dict[str, object]:
    return json.loads(
        Path("schema/DashboardHumanReviewRecord.schema.json").read_text(encoding="utf-8")
    )


def test_dashboard_review_template_is_valid() -> None:
    record = {
        "schema_version": "dashboard-human-review-v1",
        "status": "pending",
        "commit": "70c99a7",
        "reviewer": "pending-accountable-reviewer",
        "reviewed_at": None,
        "scope": {
            "routes": ["/"],
            "browsers": ["Chromium"],
            "operating_systems": ["macOS"],
            "assistive_technology": ["pending"],
            "provenance": False,
        },
        "findings": [],
        "evidence_artifacts": [],
        "remediation_or_waiver": None,
        "approval_scope": None,
    }

    errors = list(Draft202012Validator(_schema()).iter_errors(record))

    assert errors == []


def test_dashboard_review_schema_rejects_unscoped_wcag_claim() -> None:
    record = {
        "schema_version": "dashboard-human-review-v1",
        "status": "approved_within_scope",
        "commit": "70c99a7",
        "reviewer": "reviewer",
        "scope": {
            "routes": ["/"],
            "browsers": ["Chromium"],
            "operating_systems": ["macOS"],
            "assistive_technology": [],
            "provenance": True,
        },
        "findings": [],
        "approval_scope": "WCAG compliant",
    }

    errors = list(Draft202012Validator(_schema()).iter_errors(record))

    assert any("not" in error.validator for error in errors)


def test_dashboard_review_document_is_optional_until_human_review_exists() -> None:
    errors = validate_review_document(
        Path.cwd(),
        "schema/DashboardHumanReviewRecord.schema.json",
        "data/derived/dashboard_review/human_review.json",
    )

    assert errors == []

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from scripts.validate_review_schemas import validate_review_document

ROUTES = [
    "/",
    "/analyses/",
    "/analyses/cognitive_vs_procedural_ratio/",
    "/automation/",
    "/crosswalks/",
    "/demonstrators/",
    "/ontologies/",
    "/readiness/",
    "/roadmap/",
    "/sources/",
    "/sources/au_mbs/",
]


def _schema() -> dict[str, object]:
    return json.loads(
        Path("schema/DashboardHumanReviewRecord.schema.json").read_text(encoding="utf-8")
    )


def _errors(record: dict[str, object]) -> list[object]:
    return list(
        Draft202012Validator(
            _schema(),
            format_checker=FormatChecker(),
        ).iter_errors(record)
    )


def test_dashboard_review_template_is_valid() -> None:
    record = {
        "schema_version": "dashboard-human-review-v1",
        "status": "pending",
        "commit": "70c99a7",
        "reviewer": "pending-accountable-reviewer",
        "reviewed_at": None,
        "automated_packet_sha256": None,
        "owner_packet_sha256": None,
        "scope": {
            "routes": ROUTES,
            "browsers": ["Chromium"],
            "operating_systems": ["macOS"],
            "assistive_technology": ["pending"],
            "provenance": False,
            "prohibited_content": False,
        },
        "findings": [],
        "evidence_artifacts": [],
        "remediation_or_waiver": None,
        "approval_scope": None,
    }

    errors = _errors(record)

    assert errors == []


def _approved_record() -> dict[str, object]:
    return {
        "schema_version": "dashboard-human-review-v1",
        "status": "approved_within_scope",
        "commit": "70c99a7",
        "reviewer": "reviewer",
        "reviewed_at": "2026-07-23T08:30:00Z",
        "automated_packet_sha256": "a" * 64,
        "owner_packet_sha256": "b" * 64,
        "scope": {
            "routes": ROUTES,
            "browsers": ["Chromium"],
            "operating_systems": ["macOS"],
            "assistive_technology": ["VoiceOver"],
            "provenance": True,
            "prohibited_content": True,
        },
        "findings": [],
        "evidence_artifacts": ["dashboard-review-evidence-123"],
        "remediation_or_waiver": None,
        "approval_scope": "Reviewed routes in Chromium on macOS with VoiceOver.",
    }


def test_dashboard_review_schema_accepts_bounded_completed_record() -> None:
    assert _errors(_approved_record()) == []


@pytest.mark.parametrize(
    "claim",
    [
        "WCAG compliant",
        "wcag compliant",
        "WcAg 2.2 CoNfOrMaNt",
        "Universally WCAG conformant",
    ],
)
def test_dashboard_review_schema_rejects_case_insensitive_unscoped_wcag_claim(
    claim: str,
) -> None:
    record = _approved_record()
    record["approval_scope"] = claim

    errors = _errors(record)

    assert any(error.validator == "not" for error in errors)


@pytest.mark.parametrize("missing_field", ["reviewed_at", "evidence_artifacts", "approval_scope"])
def test_dashboard_review_schema_requires_completed_approval_evidence(
    missing_field: str,
) -> None:
    record = _approved_record()
    del record[missing_field]

    errors = _errors(record)

    assert any(error.validator == "required" for error in errors)


def test_dashboard_review_schema_rejects_empty_approval_evidence() -> None:
    record = _approved_record()
    record["reviewed_at"] = None
    record["evidence_artifacts"] = []
    record["approval_scope"] = ""

    validators = {error.validator for error in _errors(record)}

    assert {"type", "minItems", "minLength"} <= validators


def test_dashboard_review_schema_requires_provenance_for_approval() -> None:
    record = _approved_record()
    scope = record["scope"]
    assert isinstance(scope, dict)
    scope["provenance"] = False

    errors = _errors(record)

    assert any(error.validator == "const" for error in errors)


def test_dashboard_review_schema_rejects_unbounded_route_subset() -> None:
    record = _approved_record()
    scope = record["scope"]
    assert isinstance(scope, dict)
    scope["routes"] = ["/"]

    assert any(error.validator == "minItems" for error in _errors(record))


def test_production_validator_checks_date_time_format(tmp_path: Path) -> None:
    record = _approved_record()
    record["reviewed_at"] = "not-a-date"
    path = tmp_path / "review.json"
    path.write_text(json.dumps(record), encoding="utf-8")

    errors = validate_review_document(
        Path.cwd(),
        "schema/DashboardHumanReviewRecord.schema.json",
        path.as_posix(),
    )

    assert any("date-time" in error for error in errors)


def test_dashboard_review_document_is_optional_until_human_review_exists() -> None:
    errors = validate_review_document(
        Path.cwd(),
        "schema/DashboardHumanReviewRecord.schema.json",
        "data/derived/dashboard_review/human_review.json",
    )

    assert errors == []

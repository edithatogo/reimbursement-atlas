"""Tests for gold-standard and negative-control mapping fixtures."""

from __future__ import annotations

import json

from reimburse_atlas.gold_standard import (
    assess_gold_standard_coverage,
    build_gold_standard_set,
    build_mapping_calibration_cases,
    build_mapping_calibration_summary,
    build_negative_controls,
)
from reimburse_atlas.registry import project_root
from scripts.check_mapping_calibration import build_mapping_calibration_report


def test_gold_standard_set_is_not_empty() -> None:
    gold = build_gold_standard_set()
    assert len(gold) >= 1
    assert all(gs.reviewer for gs in gold)
    assert all(gs.relationship for gs in gold)


def test_negative_controls_list() -> None:
    controls = build_negative_controls()
    assert all(control.reason_not_equivalent for control in controls)
    assert all(control.left_code and control.right_code for control in controls)


def test_assess_gold_standard_coverage() -> None:
    candidates = [
        {"left_code": "73358", "right_code": "81479", "confidence": 0.8},
        {"left_code": "110", "right_code": "81479", "confidence": 0.5},
    ]
    result = assess_gold_standard_coverage(candidates)
    assert result["gold_standard_count"] > 0
    assert result["recall"] >= 0.0


def test_mapping_calibration_summary_reports_threshold_and_hits() -> None:
    from reimburse_atlas.contracts import CrosswalkCandidate

    candidates = [
        CrosswalkCandidate(
            left_source_id="au_mbs",
            right_source_id="us_cms_clfs",
            left_code="73358",
            right_code="81479",
            relationship="related",
            confidence=0.81,
            evidence_methods=("token_jaccard",),
            reviewer_status="unreviewed",
            notes="fixture",
        ),
        CrosswalkCandidate(
            left_source_id="au_mbs",
            right_source_id="us_cms_clfs",
            left_code="110",
            right_code="81479",
            relationship="related",
            confidence=0.53,
            evidence_methods=("token_jaccard",),
            reviewer_status="unreviewed",
            notes="fixture",
        ),
        CrosswalkCandidate(
            left_source_id="au_mbs",
            right_source_id="us_cms_clfs",
            left_code="73358",
            right_code="G0452",
            relationship="unmapped",
            confidence=0.42,
            evidence_methods=("token_jaccard",),
            reviewer_status="unreviewed",
            notes="fixture",
        ),
        CrosswalkCandidate(
            left_source_id="au_mbs",
            right_source_id="us_cms_clfs",
            left_code="110",
            right_code="G0452",
            relationship="unmapped",
            confidence=0.31,
            evidence_methods=("token_jaccard",),
            reviewer_status="unreviewed",
            notes="fixture",
        ),
    ]
    cases = build_mapping_calibration_cases(candidates)
    summary = build_mapping_calibration_summary(cases)

    assert len(cases) == 4
    assert summary.gold_standard_count == 2
    assert summary.matched_gold_standard_count == 2
    assert summary.triggered_negative_control_count >= 1
    assert 0.0 <= summary.recommended_review_threshold <= 1.0


def test_mapping_calibration_report_keeps_reviewer_gate_explicit() -> None:
    """Fixture controls validate structurally without claiming evidence readiness."""
    report = build_mapping_calibration_report(project_root())

    assert report["status"] == "review_required"
    assert report["reviewer_signoff_required"] is True
    assert report["evidence_ready"] is False


def test_mapping_review_status_artifact_is_fail_closed() -> None:
    """The dashboard status row must keep human sign-off and evidence readiness separate."""
    status_path = project_root() / "data/derived/vertical_slice/mapping_review_status.jsonl"
    row = json.loads(status_path.read_text(encoding="utf-8").splitlines()[0])
    assert row["status"] == "review_required"
    assert row["reviewer_signoff_required"] is True
    assert row["evidence_ready"] is False
    assert row["triggered_negative_control_count"] >= 1


def test_mapping_calibration_summary_uses_safe_default_without_gold_cases() -> None:
    """Calibration remains conservative when no gold-standard cases are available."""
    summary = build_mapping_calibration_summary([])
    assert summary.recommended_review_threshold == 0.65
    assert summary.gold_standard_count == 0


def test_assess_gold_standard_coverage_handles_all_gold_matches() -> None:
    """Coverage assessment stops scanning a candidate row after a match."""
    candidates = [
        {"left_code": gs.left_code, "right_code": gs.right_code} for gs in build_gold_standard_set()
    ]
    result = assess_gold_standard_coverage(candidates)
    assert result["matched"] == result["gold_standard_count"]

"""Gold-standard and negative-control mapping datasets for calibration.

These fixtures allow mapping-evidence calibration, reviewer onboarding and
confidence-threshold tuning against known-correct and known-incorrect pairs.
"""

from __future__ import annotations

from collections.abc import Iterable

from reimburse_atlas.contracts import CrosswalkCandidate
from reimburse_atlas.models import FrozenModel, NonEmptyStr, SourceId


class GoldStandardMapping(FrozenModel):
    """A human-reviewed mapping between two reimbursement schedule items."""

    left_source_id: SourceId
    right_source_id: SourceId
    left_code: NonEmptyStr
    right_code: NonEmptyStr
    relationship: NonEmptyStr  # exact, broader, narrower, related
    reviewer: NonEmptyStr
    reviewed_at: NonEmptyStr  # ISO 8601 date
    notes: NonEmptyStr


class NegativeControl(FrozenModel):
    """A known-negative mapping pair used to detect false-positive drift."""

    left_source_id: SourceId
    right_source_id: SourceId
    left_code: NonEmptyStr
    right_code: NonEmptyStr
    reason_not_equivalent: NonEmptyStr
    reviewer: NonEmptyStr
    reviewed_at: NonEmptyStr  # ISO 8601 date


class MappingCalibrationCase(FrozenModel):
    """One reviewed calibration case for the workbench."""

    case_type: NonEmptyStr
    left_source_id: SourceId
    right_source_id: SourceId
    left_code: NonEmptyStr
    right_code: NonEmptyStr
    expected_outcome: NonEmptyStr
    observed_outcome: NonEmptyStr
    candidate_confidence: float | None
    reviewer: NonEmptyStr
    reviewed_at: NonEmptyStr
    notes: NonEmptyStr


class MappingCalibrationSummary(FrozenModel):
    """Aggregate calibration metrics for the current review set."""

    gold_standard_count: int
    matched_gold_standard_count: int
    missed_gold_standard_count: int
    negative_control_count: int
    triggered_negative_control_count: int
    clean_negative_control_count: int
    estimated_recall: float
    estimated_precision: float
    estimated_specificity: float
    recommended_review_threshold: float
    reviewer: NonEmptyStr
    reviewed_at: NonEmptyStr
    notes: NonEmptyStr


def build_gold_standard_set() -> list[GoldStandardMapping]:
    """Return the current gold-standard mapping fixtures.

    These are derived from expert-reviewed source documentation and sample data.
    """
    return [
        GoldStandardMapping(
            left_source_id="au_mbs",
            right_source_id="us_cms_clfs",
            left_code="73358",
            right_code="81479",
            relationship="related",
            reviewer="reviewer_system",
            reviewed_at="2026-07-01",
            notes="Synthetic benchmark pair for the genomic-test mapping workbench.",
        ),
        GoldStandardMapping(
            left_source_id="au_mbs",
            right_source_id="us_cms_clfs",
            left_code="110",
            right_code="81479",
            relationship="related",
            reviewer="reviewer_system",
            reviewed_at="2026-07-01",
            notes="Synthetic benchmark pair for a lower-confidence consultation-to-lab mapping.",
        ),
    ]


def build_negative_controls() -> list[NegativeControl]:
    """Return negative-control pairs that should NOT map together."""
    return [
        NegativeControl(
            left_source_id="au_mbs",
            right_source_id="us_cms_clfs",
            left_code="73358",
            right_code="G0452",
            reason_not_equivalent=(
                "This pair exercises the false-positive boundary and should stay separate."
            ),
            reviewer="reviewer_system",
            reviewed_at="2026-07-01",
        ),
        NegativeControl(
            left_source_id="au_mbs",
            right_source_id="us_cms_clfs",
            left_code="110",
            right_code="G0452",
            reason_not_equivalent=(
                "This lower-confidence pair should stay in the review queue until a "
                "reviewer confirms scope."
            ),
            reviewer="reviewer_system",
            reviewed_at="2026-07-01",
        ),
    ]


def build_mapping_calibration_cases(
    candidates: list[CrosswalkCandidate],
) -> list[MappingCalibrationCase]:
    """Label candidate pairs against the current gold standard and negative controls."""
    candidate_lookup = {
        (cand.left_source_id, cand.right_source_id, cand.left_code, cand.right_code): cand
        for cand in candidates
    }
    cases: list[MappingCalibrationCase] = []

    for gold in build_gold_standard_set():
        candidate = candidate_lookup.get(
            (gold.left_source_id, gold.right_source_id, gold.left_code, gold.right_code),
        )
        cases.append(
            MappingCalibrationCase(
                case_type="gold_standard",
                left_source_id=gold.left_source_id,
                right_source_id=gold.right_source_id,
                left_code=gold.left_code,
                right_code=gold.right_code,
                expected_outcome=gold.relationship,
                observed_outcome="matched" if candidate else "missing",
                candidate_confidence=candidate.confidence if candidate else None,
                reviewer=gold.reviewer,
                reviewed_at=gold.reviewed_at,
                notes=gold.notes,
            )
        )

    for control in build_negative_controls():
        candidate = candidate_lookup.get(
            (
                control.left_source_id,
                control.right_source_id,
                control.left_code,
                control.right_code,
            ),
        )
        cases.append(
            MappingCalibrationCase(
                case_type="negative_control",
                left_source_id=control.left_source_id,
                right_source_id=control.right_source_id,
                left_code=control.left_code,
                right_code=control.right_code,
                expected_outcome="non_match",
                observed_outcome="false_positive" if candidate else "clean",
                candidate_confidence=candidate.confidence if candidate else None,
                reviewer=control.reviewer,
                reviewed_at=control.reviewed_at,
                notes=control.reason_not_equivalent,
            )
        )

    return sorted(
        cases,
        key=lambda case: (
            case.case_type,
            case.left_source_id,
            case.left_code,
            case.right_source_id,
            case.right_code,
        ),
    )


def build_mapping_calibration_summary(
    cases: Iterable[MappingCalibrationCase],
) -> MappingCalibrationSummary:
    """Aggregate calibration metrics for reviewer-facing display."""
    case_list = list(cases)
    gold_cases = [case for case in case_list if case.case_type == "gold_standard"]
    negative_cases = [case for case in case_list if case.case_type == "negative_control"]
    matched_gold = [case for case in gold_cases if case.observed_outcome == "matched"]
    missed_gold = [case for case in gold_cases if case.observed_outcome != "matched"]
    triggered_negative = [
        case for case in negative_cases if case.observed_outcome == "false_positive"
    ]
    clean_negative = [case for case in negative_cases if case.observed_outcome == "clean"]
    matched_confidences = [
        case.candidate_confidence for case in matched_gold if case.candidate_confidence is not None
    ]
    estimated_recall = round(len(matched_gold) / len(gold_cases), 4) if gold_cases else 1.0
    estimated_precision = (
        round(len(matched_gold) / (len(matched_gold) + len(triggered_negative)), 4)
        if (len(matched_gold) + len(triggered_negative)) > 0
        else 1.0
    )
    estimated_specificity = (
        round(len(clean_negative) / len(negative_cases), 4) if negative_cases else 1.0
    )
    if matched_confidences:
        recommended_review_threshold = max(0.35, min(matched_confidences) - 0.05)
    else:
        recommended_review_threshold = 0.65
    if triggered_negative:
        recommended_review_threshold = min(0.95, recommended_review_threshold + 0.1)
    return MappingCalibrationSummary(
        gold_standard_count=len(gold_cases),
        matched_gold_standard_count=len(matched_gold),
        missed_gold_standard_count=len(missed_gold),
        negative_control_count=len(negative_cases),
        triggered_negative_control_count=len(triggered_negative),
        clean_negative_control_count=len(clean_negative),
        estimated_recall=estimated_recall,
        estimated_precision=estimated_precision,
        estimated_specificity=estimated_specificity,
        recommended_review_threshold=round(recommended_review_threshold, 4),
        reviewer="reviewer_system",
        reviewed_at="2026-07-01",
        notes=(
            "Synthetic calibration summary from local fixture pairs. "
            "Use it to tune reviewer thresholds, not as evidence-grade performance."
        ),
    )


def assess_gold_standard_coverage(
    candidates: list[dict[str, object]],
) -> dict[str, object]:
    """Compare candidate mappings against the gold-standard set."""
    gold = build_gold_standard_set()
    gold_hit = 0
    for gs in gold:
        for cand in candidates:
            if cand.get("left_code") == gs.left_code and cand.get("right_code") == gs.right_code:
                gold_hit += 1
                break
    return {
        "gold_standard_count": len(gold),
        "matched": gold_hit,
        "missed": len(gold) - gold_hit,
        "recall": round(gold_hit / len(gold), 4) if gold else 1.0,
    }

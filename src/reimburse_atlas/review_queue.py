"""Review-queue helpers for machine-generated mappings."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from reimburse_atlas.contracts import CrosswalkCandidate


@dataclass(frozen=True)
class CrosswalkReviewRecord:
    """Human-review queue row for a candidate mapping."""

    left_source_id: str
    right_source_id: str
    left_code: str
    right_code: str
    relationship: str
    confidence: float
    priority: Literal["high", "medium", "low"]
    recommended_action: Literal["domain_review", "triage", "park"]
    evidence_methods: str
    review_note: str


def review_priority(candidate: CrosswalkCandidate) -> Literal["high", "medium", "low"]:
    """Assign a review priority from confidence and relationship."""
    if candidate.relationship == "exact" or candidate.confidence >= 0.75:
        return "high"
    if candidate.relationship == "related" or candidate.confidence >= 0.35:
        return "medium"
    return "low"


def recommended_action(candidate: CrosswalkCandidate) -> Literal["domain_review", "triage", "park"]:
    """Suggest the next human action for a candidate mapping."""
    priority = review_priority(candidate)
    if priority == "high":
        return "domain_review"
    if priority == "medium":
        return "triage"
    return "park"


def build_crosswalk_review_queue(
    candidates: list[CrosswalkCandidate],
) -> list[CrosswalkReviewRecord]:
    """Convert crosswalk candidates into deterministic human-review rows."""
    records: list[CrosswalkReviewRecord] = []
    for candidate in candidates:
        priority = review_priority(candidate)
        records.append(
            CrosswalkReviewRecord(
                left_source_id=candidate.left_source_id,
                right_source_id=candidate.right_source_id,
                left_code=candidate.left_code,
                right_code=candidate.right_code,
                relationship=candidate.relationship,
                confidence=candidate.confidence,
                priority=priority,
                recommended_action=recommended_action(candidate),
                evidence_methods=";".join(candidate.evidence_methods),
                review_note=(
                    "Do not use in policy estimates until a domain reviewer confirms scope, "
                    "code semantics, setting and unit equivalence."
                ),
            )
        )
    return sorted(
        records,
        key=lambda record: (
            {"high": 0, "medium": 1, "low": 2}[record.priority],
            -record.confidence,
            record.left_code,
            record.right_code,
        ),
    )


def review_rows(records: list[CrosswalkReviewRecord]) -> list[dict[str, object]]:
    """Serialise review queue records to dictionaries."""
    return [asdict(record) for record in records]

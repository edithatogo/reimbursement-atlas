"""Deterministic candidate crosswalk generation for tiny review queues."""

from __future__ import annotations

import re

from reimburse_atlas.contracts import CrosswalkCandidate, CrosswalkRelationship, ScheduleItemRecord

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "and",
    "for",
    "of",
    "the",
    "to",
    "with",
    "without",
    "item",
    "procedure",
    "service",
    "test",
}


def tokens(text: str) -> frozenset[str]:
    """Tokenise text for conservative label similarity."""
    return frozenset(
        token for token in TOKEN_PATTERN.findall(text.lower()) if token not in STOPWORDS
    )


def jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    """Return Jaccard similarity for token sets."""
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def relationship_for_similarity(score: float) -> CrosswalkRelationship:
    """Map a similarity score to an auditable relationship label."""
    if score >= 0.92:
        return "exact"
    if score >= 0.55:
        return "related"
    return "unmapped"


def build_crosswalk_candidates(
    left_records: list[ScheduleItemRecord],
    right_records: list[ScheduleItemRecord],
    *,
    threshold: float = 0.2,
) -> list[CrosswalkCandidate]:
    """Build machine-generated crosswalk candidates from item labels.

    The output is intentionally a review queue, not a final crosswalk. It uses a
    transparent token overlap baseline so later embedding/LanceDB approaches can
    be benchmarked against a simple deterministic method.
    """
    candidates: list[CrosswalkCandidate] = []
    for left in left_records:
        left_tokens = tokens(f"{left.item_label} {left.item_description or ''}")
        for right in right_records:
            right_tokens = tokens(f"{right.item_label} {right.item_description or ''}")
            score = jaccard(left_tokens, right_tokens)
            if score < threshold:
                continue
            candidates.append(
                CrosswalkCandidate(
                    left_source_id=left.source_id,
                    right_source_id=right.source_id,
                    left_code=left.item_code,
                    right_code=right.item_code,
                    relationship=relationship_for_similarity(score),
                    confidence=round(score, 3),
                    evidence_methods=("token_jaccard",),
                    reviewer_status="unreviewed",
                    notes="Machine-generated candidate; requires domain review before policy use.",
                )
            )
    return sorted(
        candidates,
        key=lambda candidate: (
            -candidate.confidence,
            candidate.left_source_id,
            candidate.left_code,
            candidate.right_source_id,
            candidate.right_code,
        ),
    )

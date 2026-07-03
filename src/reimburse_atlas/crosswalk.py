"""Candidate crosswalk generation for reimbursement item mapping."""

from __future__ import annotations

import re
from collections.abc import Iterable

from reimburse_atlas.contracts import CrosswalkCandidate, CrosswalkRelationship, ScheduleItemRecord

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "and",
    "for",
    "of",
    "the",
    "with",
    "without",
    "initial",
    "subsequent",
    "service",
    "services",
    "procedure",
    "item",
}


def normalise_text(value: str) -> str:
    """Normalise text for transparent deterministic matching."""
    return " ".join(tokenise(value))


def tokenise(value: str) -> tuple[str, ...]:
    """Tokenise text and remove generic stopwords."""
    return tuple(
        token for token in TOKEN_PATTERN.findall(value.lower()) if token and token not in STOPWORDS
    )


def jaccard_similarity(left: Iterable[str], right: Iterable[str]) -> float:
    """Return Jaccard similarity over token sets."""
    left_set = set(left)
    right_set = set(right)
    if not left_set and not right_set:
        return 1.0
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(left_set | right_set)


def candidate_relationship(score: float) -> CrosswalkRelationship:
    """Convert a confidence score to a coarse mapping relationship."""
    if score >= 0.92:
        return "exact"
    if score >= 0.55:
        return "related"
    return "unmapped"


def generate_crosswalk_candidates(
    left_items: list[ScheduleItemRecord],
    right_items: list[ScheduleItemRecord],
    *,
    threshold: float = 0.2,
    max_candidates_per_left: int = 3,
) -> list[CrosswalkCandidate]:
    """Generate transparent token-overlap crosswalk candidates.

    This is a review-queue generator, not an automated mapping authority. Later
    versions can add embeddings, LOINC/ATC/UMLS evidence, and clinician review.
    """
    candidates: list[CrosswalkCandidate] = []
    for left in left_items:
        scored: list[tuple[float, ScheduleItemRecord]] = []
        left_tokens = tokenise(" ".join([left.item_label, left.item_description or ""]))
        for right in right_items:
            if left.domain != right.domain:
                continue
            right_tokens = tokenise(" ".join([right.item_label, right.item_description or ""]))
            score = jaccard_similarity(left_tokens, right_tokens)
            if score >= threshold:
                scored.append((score, right))
        for score, right in sorted(scored, key=lambda item: (-item[0], item[1].item_code))[
            :max_candidates_per_left
        ]:
            candidates.append(
                CrosswalkCandidate(
                    left_source_id=left.source_id,
                    right_source_id=right.source_id,
                    left_code=left.item_code,
                    right_code=right.item_code,
                    relationship=candidate_relationship(score),
                    confidence=round(score, 4),
                    evidence_methods=("token_jaccard", "domain_filter"),
                    notes=(
                        "Machine-generated candidate for human review; not a definitive billing "
                        "or clinical equivalence statement."
                    ),
                )
            )
    return candidates

"""Transparent mapping-evidence features for cross-jurisdiction candidate review."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Iterable
from typing import Annotated

from pydantic import Field

from reimburse_atlas.contracts import ScheduleItemRecord
from reimburse_atlas.crosswalk import jaccard_similarity, tokenise
from reimburse_atlas.models import FrozenModel, NonEmptyStr, SourceId

Confidence = Annotated[float, Field(ge=0.0, le=1.0)]


class MappingEvidenceRecord(FrozenModel):
    """Feature row used to explain a candidate reimbursement crosswalk."""

    left_source_id: SourceId
    right_source_id: SourceId
    left_code: NonEmptyStr
    right_code: NonEmptyStr
    token_jaccard: Confidence
    hash_cosine: Confidence
    price_ratio: float | None = Field(default=None, ge=0.0)
    same_domain: bool
    same_currency: bool
    confidence: Confidence
    review_priority: Annotated[int, Field(ge=1, le=5)]
    evidence_methods: tuple[NonEmptyStr, ...]
    notes: NonEmptyStr


def build_mapping_evidence_matrix(
    left_items: list[ScheduleItemRecord],
    right_items: list[ScheduleItemRecord],
    *,
    threshold: float = 0.05,
    vector_dimensions: int = 48,
    max_candidates_per_left: int = 5,
) -> list[MappingEvidenceRecord]:
    """Build reviewable feature rows for two groups of schedule items."""
    rows: list[MappingEvidenceRecord] = []
    for left in left_items:
        candidates: list[MappingEvidenceRecord] = []
        left_text = _record_text(left)
        left_tokens = tokenise(left_text)
        left_vector = hash_text_vector(left_text, dimensions=vector_dimensions)
        for right in right_items:
            right_text = _record_text(right)
            token_score = jaccard_similarity(left_tokens, tokenise(right_text))
            vector_score = cosine_similarity(
                left_vector,
                hash_text_vector(right_text, dimensions=vector_dimensions),
            )
            if max(token_score, vector_score) < threshold:
                continue
            price_ratio = _price_ratio(left.payment_amount, right.payment_amount)
            same_domain = left.domain == right.domain
            same_currency = left.currency is not None and left.currency == right.currency
            confidence = _combined_confidence(
                token_score=token_score,
                vector_score=vector_score,
                same_domain=same_domain,
                price_ratio=price_ratio,
            )
            candidates.append(
                MappingEvidenceRecord(
                    left_source_id=left.source_id,
                    right_source_id=right.source_id,
                    left_code=left.item_code,
                    right_code=right.item_code,
                    token_jaccard=round(token_score, 4),
                    hash_cosine=round(vector_score, 4),
                    price_ratio=round(price_ratio, 4) if price_ratio is not None else None,
                    same_domain=same_domain,
                    same_currency=same_currency,
                    confidence=round(confidence, 4),
                    review_priority=_review_priority(confidence, same_domain=same_domain),
                    evidence_methods=("token_jaccard", "hash_vector_cosine", "price_ratio"),
                    notes=(
                        "Machine-generated mapping evidence; suitable for triage only until "
                        "domain and terminology review are complete."
                    ),
                )
            )
        rows.extend(
            sorted(
                candidates,
                key=lambda row: (-row.confidence, row.right_source_id, row.right_code),
            )[:max_candidates_per_left]
        )
    return sorted(
        rows,
        key=lambda row: (
            row.left_source_id,
            row.left_code,
            -row.confidence,
            row.right_source_id,
            row.right_code,
        ),
    )


def hash_text_vector(text: str, *, dimensions: int = 48) -> tuple[float, ...]:
    """Create a deterministic lexical vector without external embedding services."""
    if dimensions <= 0:
        msg = "dimensions must be positive"
        raise ValueError(msg)
    vector = [0.0] * dimensions
    for token in tokenise(text):
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], byteorder="big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    if norm <= 0.0:
        return tuple(vector)
    return tuple(value / norm for value in vector)


def cosine_similarity(left: Iterable[float], right: Iterable[float]) -> float:
    """Return a bounded cosine similarity rescaled to 0..1."""
    left_values = tuple(left)
    right_values = tuple(right)
    if len(left_values) != len(right_values):
        msg = "vectors must have the same dimensionality"
        raise ValueError(msg)
    if not left_values:
        return 0.0
    raw = sum(
        left_value * right_value
        for left_value, right_value in zip(left_values, right_values, strict=True)
    )
    return max(0.0, min(1.0, (raw + 1.0) / 2.0))


def _record_text(record: ScheduleItemRecord) -> str:
    return " ".join(
        part
        for part in (
            record.item_label,
            record.item_description,
            record.restriction_text,
            record.setting,
            record.domain,
        )
        if part
    )


def _price_ratio(left: float | None, right: float | None) -> float | None:
    if left is None or right is None or left <= 0.0 or right <= 0.0:
        return None
    return max(left, right) / min(left, right)


def _combined_confidence(
    *,
    token_score: float,
    vector_score: float,
    same_domain: bool,
    price_ratio: float | None,
) -> float:
    domain_bonus = 0.08 if same_domain else -0.08
    price_bonus = 0.0
    if price_ratio is not None:
        if price_ratio <= 2.0:
            price_bonus = 0.05
        elif price_ratio >= 20.0:
            price_bonus = -0.05
    weighted_score = (0.55 * token_score) + (0.45 * vector_score)
    return max(0.0, min(1.0, weighted_score + domain_bonus + price_bonus))


def _review_priority(confidence: float, *, same_domain: bool) -> int:
    if confidence >= 0.75 and same_domain:
        return 1
    if confidence >= 0.55:
        return 2
    if confidence >= 0.35:
        return 3
    if confidence >= 0.2:
        return 4
    return 5

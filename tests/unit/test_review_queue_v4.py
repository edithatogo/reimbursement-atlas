"""Tests for crosswalk review queue helpers."""

from __future__ import annotations

from reimburse_atlas.contracts import CrosswalkCandidate
from reimburse_atlas.review_queue import build_crosswalk_review_queue, review_rows


def test_crosswalk_review_queue_prioritises_high_confidence_candidates() -> None:
    """High-confidence candidates should be routed to domain review."""
    records = build_crosswalk_review_queue([
        CrosswalkCandidate(
            left_source_id="au_mbs",
            right_source_id="us_cms_clfs",
            left_code="1",
            right_code="A",
            relationship="related",
            confidence=0.8,
            evidence_methods=("token_jaccard",),
        ),
        CrosswalkCandidate(
            left_source_id="au_mbs",
            right_source_id="us_cms_clfs",
            left_code="2",
            right_code="B",
            relationship="unmapped",
            confidence=0.1,
            evidence_methods=("token_jaccard",),
        ),
    ])
    assert records[0].priority == "high"
    assert records[0].recommended_action == "domain_review"
    assert records[-1].priority == "low"
    assert review_rows(records)[0]["left_code"] == "1"

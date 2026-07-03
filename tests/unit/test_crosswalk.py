"""Tests for deterministic crosswalk candidate generation."""

from __future__ import annotations

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord
from reimburse_atlas.crosswalk import generate_crosswalk_candidates, jaccard_similarity, tokenise


def _item(source_id: str, code: str, label: str, domain: str = "laboratory") -> ScheduleItemRecord:
    return ScheduleItemRecord(
        source_id=source_id,
        jurisdiction="X",
        domain=domain,
        code_system="TEST",
        item_code=code,
        item_label=label,
        currency="USD",
        provenance=ProvenanceRecord(source_id=source_id),
    )


def test_tokenise_removes_generic_stopwords() -> None:
    """Tokenisation should keep discriminating content words."""
    assert tokenise("Initial genomic test for rare disease") == (
        "genomic",
        "test",
        "rare",
        "disease",
    )


def test_jaccard_similarity_bounds() -> None:
    """Jaccard similarity should be bounded and intuitive."""
    assert jaccard_similarity(("a",), ("a",)) == 1.0
    assert jaccard_similarity(("a",), ("b",)) == 0.0


def test_generate_crosswalk_candidates_filters_by_domain() -> None:
    """Candidate generation should not map across incompatible domains."""
    left = [_item("au_mbs", "A", "rare disease genomic panel")]
    right = [
        _item("us_cms_clfs", "B", "genomic rare disease panel"),
        _item("au_pbs", "C", "rare disease medicine", domain="medicines"),
    ]
    candidates = generate_crosswalk_candidates(left, right, threshold=0.2)
    assert len(candidates) == 1
    assert candidates[0].right_code == "B"
    assert candidates[0].confidence > 0.5

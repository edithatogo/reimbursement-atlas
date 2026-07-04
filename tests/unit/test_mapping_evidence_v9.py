"""Tests for deterministic mapping-evidence feature rows."""

from __future__ import annotations

import pytest

from reimburse_atlas.analysis.mapping_evidence import (
    build_mapping_evidence_matrix,
    cosine_similarity,
    hash_text_vector,
)
from reimburse_atlas.parsers import parse_cms_clfs_csv, parse_cms_pfs_csv, parse_mbs_xml
from reimburse_atlas.registry import project_root
from reimburse_atlas.vector_index import schedule_item_vector_rows


def test_hash_text_vector_is_deterministic_and_normalised() -> None:
    left = hash_text_vector("genomic chromosome microarray", dimensions=16)
    right = hash_text_vector("genomic chromosome microarray", dimensions=16)

    assert left == right
    assert len(left) == 16
    assert cosine_similarity(left, right) == pytest.approx(1.0)


def test_mapping_evidence_matrix_produces_reviewable_rows() -> None:
    fixtures = project_root() / "tests" / "fixtures"
    mbs_records = parse_mbs_xml(fixtures / "mbs_fragment.xml")
    clfs_records = parse_cms_clfs_csv(fixtures / "cms_clfs_fixture.csv")
    pfs_records = parse_cms_pfs_csv(fixtures / "cms_pfs_fixture.csv")

    rows = build_mapping_evidence_matrix(mbs_records, [*clfs_records, *pfs_records], threshold=0.05)

    assert rows
    assert {row.left_source_id for row in rows} == {"au_mbs"}
    assert all(1 <= row.review_priority <= 5 for row in rows)
    assert all("hash_vector_cosine" in row.evidence_methods for row in rows)


def test_schedule_item_vector_rows_are_lancedb_ready() -> None:
    fixtures = project_root() / "tests" / "fixtures"
    records = parse_mbs_xml(fixtures / "mbs_fragment.xml")

    rows = schedule_item_vector_rows(records, dimensions=12)

    assert rows
    assert len(rows[0]["vector"]) == 12
    assert rows[0]["source_id"] == "au_mbs"


def test_mapping_evidence_branch_helpers() -> None:
    from reimburse_atlas.analysis.mapping_evidence import (
        _combined_confidence,  # noqa: PLC2701
        _price_ratio,  # noqa: PLC2701
        _review_priority,  # noqa: PLC2701
    )

    assert _price_ratio(None, 1.0) is None
    assert _price_ratio(0.0, 2.0) is None
    assert _price_ratio(2.0, 10.0) == pytest.approx(5.0)
    assert (
        _combined_confidence(
            token_score=0.9,
            vector_score=0.9,
            same_domain=True,
            price_ratio=1.2,
        )
        > 0.9
    )
    assert (
        _combined_confidence(
            token_score=0.1,
            vector_score=0.1,
            same_domain=False,
            price_ratio=30.0,
        )
        >= 0.0
    )
    assert _review_priority(0.8, same_domain=True) == 1
    assert _review_priority(0.1, same_domain=False) == 5


def test_cosine_similarity_rejects_dimension_mismatch() -> None:
    with pytest.raises(ValueError, match="same dimensionality"):
        cosine_similarity((1.0,), (1.0, 2.0))


def test_hash_text_vector_rejects_non_positive_dimensions() -> None:
    with pytest.raises(ValueError, match="positive"):
        hash_text_vector("text", dimensions=0)

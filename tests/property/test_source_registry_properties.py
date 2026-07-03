"""Property tests for registry quality helpers."""

from __future__ import annotations

import pytest

pytest.importorskip("hypothesis")

from hypothesis import given
from hypothesis import strategies as st

from reimburse_atlas.quality import duplicate_source_ids


@given(
    st.lists(
        st.text(alphabet=st.characters(whitelist_categories=("Ll", "Nd")), min_size=1),
        min_size=1,
        max_size=20,
    ),
)
def test_duplicate_source_ids_is_sorted(ids: list[str]) -> None:
    """Duplicate id output should be sorted."""
    records = [type("R", (), {"id": item})() for item in ids]
    duplicates = duplicate_source_ids(records)  # type: ignore[arg-type]
    assert duplicates == sorted(duplicates)

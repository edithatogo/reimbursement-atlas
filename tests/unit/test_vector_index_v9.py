"""Tests for v9 Arrow/LanceDB vector-index helpers."""

from __future__ import annotations

import importlib.util

import pytest

from reimburse_atlas.parsers import parse_mbs_xml
from reimburse_atlas.registry import project_root
from reimburse_atlas.vector_index import (
    build_lancedb_index,
    schedule_item_vector_rows,
    write_arrow_vector_seed,
)


def test_write_arrow_vector_seed_when_pyarrow_available(tmp_path) -> None:  # type: ignore[no-untyped-def]
    if importlib.util.find_spec("pyarrow") is None:
        pytest.skip("pyarrow not installed")
    records = parse_mbs_xml(project_root() / "tests" / "fixtures" / "mbs_fragment.xml")
    rows = schedule_item_vector_rows(records, dimensions=8)

    path = write_arrow_vector_seed(rows, tmp_path / "vectors.arrow")

    assert path.exists()
    assert path.stat().st_size > 0


def test_build_lancedb_index_when_lancedb_available(tmp_path) -> None:  # type: ignore[no-untyped-def]
    if importlib.util.find_spec("lancedb") is None:
        pytest.skip("lancedb not installed")
    records = parse_mbs_xml(project_root() / "tests" / "fixtures" / "mbs_fragment.xml")
    rows = schedule_item_vector_rows(records, dimensions=8)

    path = build_lancedb_index(rows, database_dir=tmp_path / "lancedb")

    assert path.exists()

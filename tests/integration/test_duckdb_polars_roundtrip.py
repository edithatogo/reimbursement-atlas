"""Integration test scaffold for DuckDB + Polars seed analysis."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("duckdb")
pytest.importorskip("polars")

import duckdb
import polars as pl


def test_source_registry_polars_duckdb_roundtrip(repo_root: Path) -> None:
    """Seed registry should load in Polars and register in DuckDB."""
    path = repo_root / "data" / "seed" / "source_registry.csv"
    frame = pl.read_csv(path)
    assert frame.height >= 50
    con = duckdb.connect(":memory:")
    con.register("sources", frame.to_arrow())
    count = con.execute("select count(*) from sources where access_tier = 'tier_1'").fetchone()[0]
    assert count > 0

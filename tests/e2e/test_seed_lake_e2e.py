"""End-to-end tests for local seed-lake materialisation."""

from __future__ import annotations

from reimburse_atlas.datalake import materialise_seed_lake


def test_materialise_seed_lake(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """The seed lake command helper should write a manifest and tables."""
    manifest = materialise_seed_lake(tmp_path / "lake")
    assert manifest.table_count >= 5
    assert (tmp_path / "lake" / "manifest.json").exists()

"""Tests for first-wave ingestion planning."""

from __future__ import annotations

from reimburse_atlas.ingest import build_first_wave_ingestion_plan
from reimburse_atlas.registry import load_source_registry, load_source_versions


def test_build_first_wave_ingestion_plan() -> None:
    """First-wave plan should include parser targets without fetching data."""
    tasks = build_first_wave_ingestion_plan(load_source_registry(), load_source_versions())
    assert tasks
    assert {task.source_id for task in tasks} >= {"au_mbs", "us_cms_clfs"}
    assert all(task.network_policy == "fixture_only" for task in tasks)
    assert all(task.priority >= 1 for task in tasks)

"""Tests for first-wave ingestion plans."""

from __future__ import annotations

from reimburse_atlas.ingestion import assess_ingestion_readiness, build_first_wave_plans
from reimburse_atlas.registry import load_source_registry, load_source_versions


def test_build_first_wave_plans_matches_registered_versions() -> None:
    """Every registered source version should get a cautious acquisition plan."""
    plans = build_first_wave_plans(load_source_registry(), load_source_versions())
    assert len(plans) == len(load_source_versions())
    assert all(plan.licence_gate for plan in plans)


def test_assess_ingestion_readiness_identifies_blockers() -> None:
    """Readiness assessment should surface licence and parser blockers."""
    plans = build_first_wave_plans(load_source_registry(), load_source_versions())
    records = assess_ingestion_readiness(plans)
    assert records
    assert any(record.blocker_count >= 1 for record in records)

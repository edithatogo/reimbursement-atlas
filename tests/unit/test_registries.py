"""Unit tests for registry loading."""

from __future__ import annotations

from reimburse_atlas.quality import (
    access_tier_counts,
    duplicate_source_ids,
    missing_analysis_sources,
    missing_source_version_sources,
)
from reimburse_atlas.registry import (
    load_analysis_catalogue,
    load_ontology_registry,
    load_source_registry,
    load_source_versions,
    source_ids,
)


def test_source_registry_loads_many_sources() -> None:
    """The seed source registry should be non-trivial."""
    records = load_source_registry()
    assert len(records) >= 60
    assert duplicate_source_ids(records) == []
    assert "tier_1" in access_tier_counts(records)


def test_pbs_registry_matches_documented_monthly_refresh() -> None:
    """Keep the PBS registry aligned with the official monthly update cadence."""
    pbs = next((record for record in load_source_registry() if record.id == "au_pbs"), None)
    assert pbs is not None, "au_pbs record not found in source registry"
    assert pbs.refresh_cadence == "monthly"


def test_analysis_sources_resolve() -> None:
    """Each analysis must reference known source ids."""
    sources = load_source_registry()
    analyses = load_analysis_catalogue()
    assert len(analyses) >= 25
    assert missing_analysis_sources(analyses, source_ids(sources)) == {}


def test_source_versions_resolve() -> None:
    """Each source version should reference a registered source."""
    sources = load_source_registry()
    versions = load_source_versions()
    assert len(versions) >= 3
    assert missing_source_version_sources(versions, source_ids(sources)) == {}


def test_ontology_registry_contains_core_terms() -> None:
    """Core biomedical ontologies should be represented in the design registry."""
    ontologies = {record.id for record in load_ontology_registry()}
    assert {"loinc", "rxnorm", "umls", "icd11", "atc", "hpo"}.issubset(ontologies)

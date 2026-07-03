"""Tests for local-only terminology concept seed helpers."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.terminologies import build_mapping_templates, parse_ontology_concepts_csv


def test_parse_ontology_concepts_fixture(repo_root: Path) -> None:
    """Synthetic ontology concepts should parse into strict records."""
    concepts = parse_ontology_concepts_csv(
        repo_root / "tests" / "fixtures" / "ontology_concepts_fixture.csv"
    )
    assert len(concepts) == 6
    assert concepts[0].terminology_id == "loinc"
    assert concepts[0].licence_scope == "synthetic"
    assert "genetic variant report" in concepts[0].synonyms


def test_build_mapping_templates_from_target_hints(repo_root: Path) -> None:
    """Mapping target hints should become reviewable templates."""
    concepts = parse_ontology_concepts_csv(
        repo_root / "tests" / "fixtures" / "ontology_concepts_fixture.csv"
    )
    templates = build_mapping_templates(concepts)
    assert len(templates) == 3
    assert {template.relationship for template in templates} == {"candidate"}

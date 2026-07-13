"""Tests for local-only terminology concept seed helpers."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.terminologies import (
    RxNavAdapterConfig,
    RxNavConceptQuery,
    build_mapping_templates,
    build_rxnav_approximate_match_url,
    parse_ontology_concepts_csv,
    parse_rxnav_matches,
)


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


def test_rxnav_adapter_contract_builds_local_only_url() -> None:
    """The adapter contract should build a request without performing network IO."""
    url = build_rxnav_approximate_match_url(
        RxNavAdapterConfig(base_url="http://localhost:8000/"),
        RxNavConceptQuery(term="amoxicillin 500 mg", max_results=5),
    )
    assert url == (
        "http://localhost:8000/REST/approximateTerm.json?term=amoxicillin+500+mg&maxEntries=5"
    )


def test_rxnav_parser_keeps_only_derived_matches() -> None:
    """Malformed and payload-heavy entries should not escape the adapter boundary."""
    matches = parse_rxnav_matches({
        "approximateGroup": {
            "candidate": [
                {"rxcui": "723", "name": "Amoxicillin 500 MG Oral Capsule", "score": "1"},
                {"rxcui": "", "name": "invalid"},
                {"name": "missing identifier"},
                "not-a-record",
            ]
        }
    })
    assert [match.model_dump() for match in matches] == [
        {"rxcui": "723", "label": "Amoxicillin 500 MG Oral Capsule"}
    ]

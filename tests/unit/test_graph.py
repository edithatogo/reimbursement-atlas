"""Tests for graph construction."""

from __future__ import annotations

from reimburse_atlas.graph import build_seed_graph, slug
from reimburse_atlas.registry import (
    load_analysis_catalogue,
    load_ontology_registry,
    load_source_registry,
    load_source_versions,
)


def test_slug_is_deterministic() -> None:
    """Slugging should be stable for graph ids."""
    assert slug("Canada - British Columbia") == "canada_british_columbia"


def test_build_seed_graph_contains_sources_and_analyses() -> None:
    """Graph should include source and analysis nodes plus required-source edges."""
    graph = build_seed_graph(
        load_source_registry(),
        load_analysis_catalogue(),
        load_ontology_registry(),
        load_source_versions(),
    )
    node_ids = {node["id"] for node in graph.nodes}
    assert "source:au_mbs" in node_ids
    assert "analysis:genomics_coverage_price_diffusion" in node_ids
    assert "version:au_mbs_seed_fixture" in node_ids
    assert any(edge["relationship"] == "requires_source" for edge in graph.edges)

"""Regenerate source-analysis-ontology graph seed files."""

from __future__ import annotations

from reimburse_atlas.graph import build_seed_graph, write_graph_csvs
from reimburse_atlas.registry import (
    load_analysis_catalogue,
    load_analysis_recipes,
    load_conductor_tracks,
    load_dataset_candidates,
    load_mapping_resources,
    load_ontology_concepts,
    load_ontology_mapping_templates,
    load_ontology_registry,
    load_output_artifact_plans,
    load_research_questions,
    load_roadmap_functions,
    load_source_files,
    load_source_registry,
    load_source_versions,
    project_root,
)


def main() -> None:
    """Build graph CSV files from seed registries."""
    graph = build_seed_graph(
        load_source_registry(),
        load_analysis_catalogue(),
        load_ontology_registry(),
        load_source_versions(),
        load_source_files(),
        load_analysis_recipes(),
        load_ontology_concepts(),
        load_ontology_mapping_templates(),
        load_conductor_tracks(),
        load_roadmap_functions(),
        load_dataset_candidates(),
        load_mapping_resources(),
        load_research_questions(),
        load_output_artifact_plans(),
    )
    nodes_path, edges_path = write_graph_csvs(graph, project_root() / "data" / "seed")
    print(f"Wrote {nodes_path} and {edges_path}")


if __name__ == "__main__":
    main()

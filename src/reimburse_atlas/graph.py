"""Graph export helpers for source-analysis-ontology exploration."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from operator import itemgetter
from pathlib import Path

from reimburse_atlas.models import (
    AnalysisRecipeRecord,
    AnalysisRecord,
    ConductorTrackRecord,
    DatasetCandidateRecord,
    MappingResourceRecord,
    OntologyRecord,
    OutputArtifactPlanRecord,
    ResearchQuestionRecord,
    RoadmapFunctionRecord,
    SourceFileRecord,
    SourceRecord,
    SourceVersionRecord,
)
from reimburse_atlas.terminologies import OntologyConceptRecord, OntologyMappingTemplate

SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class GraphTables:
    """Node and edge tables for the seed graph."""

    nodes: list[dict[str, str]]
    edges: list[dict[str, str]]


def slug(value: str) -> str:
    """Create a deterministic lowercase slug."""
    cleaned = SLUG_PATTERN.sub("_", value.lower()).strip("_")
    return cleaned or "unknown"


def _node(node_id: str, label: str, kind: str, **attrs: str) -> dict[str, str]:
    row = {"id": node_id, "label": label, "kind": kind}
    row.update({key: value for key, value in attrs.items() if value})
    return row


def _edge(source: str, target: str, relationship: str) -> dict[str, str]:
    return {"source": source, "target": target, "relationship": relationship}


def build_seed_graph(  # noqa: PLR0912, PLR0914, PLR0915
    sources: list[SourceRecord],
    analyses: list[AnalysisRecord],
    ontologies: list[OntologyRecord],
    versions: list[SourceVersionRecord] | None = None,
    source_files: list[SourceFileRecord] | None = None,
    recipes: list[AnalysisRecipeRecord] | None = None,
    ontology_concepts: list[OntologyConceptRecord] | None = None,
    ontology_mapping_templates: list[OntologyMappingTemplate] | None = None,
    conductor_tracks: list[ConductorTrackRecord] | None = None,
    roadmap_functions: list[RoadmapFunctionRecord] | None = None,
    dataset_candidates: list[DatasetCandidateRecord] | None = None,
    mapping_resources: list[MappingResourceRecord] | None = None,
    research_questions: list[ResearchQuestionRecord] | None = None,
    output_plans: list[OutputArtifactPlanRecord] | None = None,
) -> GraphTables:
    """Build a lightweight graph from the seed registries."""
    nodes_by_id: dict[str, dict[str, str]] = {}
    edges: list[dict[str, str]] = []

    def add_node(row: dict[str, str]) -> None:
        nodes_by_id.setdefault(row["id"], row)

    for source in sources:
        source_node = f"source:{source.id}"
        jurisdiction_node = f"jurisdiction:{slug(source.jurisdiction)}"
        domain_node = f"domain:{slug(source.domain)}"
        add_node(
            _node(
                source_node,
                source.schedule,
                "source",
                jurisdiction=source.jurisdiction,
                domain=source.domain,
                access_tier=source.access_tier,
            ),
        )
        add_node(_node(jurisdiction_node, source.jurisdiction, "jurisdiction"))
        add_node(_node(domain_node, source.domain, "domain"))
        edges.extend((
            _edge(source_node, jurisdiction_node, "in_jurisdiction"),
            _edge(source_node, domain_node, "covers_domain"),
        ))

    for version in versions or []:
        version_node = f"version:{version.id}"
        add_node(
            _node(
                version_node,
                version.version_label,
                "source_version",
                parser_status=version.parser_status,
                format=version.format,
            ),
        )
        edges.append(_edge(version_node, f"source:{version.source_id}", "version_of"))

    for source_file in source_files or []:
        file_node = f"source_file:{source_file.id}"
        add_node(
            _node(
                file_node,
                source_file.file_label,
                "source_file",
                file_role=source_file.file_role,
                acquisition_mode=source_file.acquisition_mode,
                licence_gate=source_file.licence_gate,
                expected_format=source_file.expected_format,
            ),
        )
        edges.extend((
            _edge(file_node, f"version:{source_file.source_version_id}", "file_for_version"),
            _edge(file_node, f"source:{source_file.source_id}", "file_for_source"),
        ))

    for analysis in analyses:
        analysis_node = f"analysis:{analysis.id}"
        add_node(
            _node(
                analysis_node,
                analysis.title,
                "analysis",
                difficulty=analysis.difficulty,
                stage=analysis.stage,
            ),
        )
        for source_id in analysis.required_sources:
            edges.append(_edge(analysis_node, f"source:{source_id}", "requires_source"))

    for recipe in recipes or []:
        recipe_node = f"recipe:{recipe.id}"
        add_node(
            _node(
                recipe_node,
                recipe.policy_question,
                "analysis_recipe",
                status=recipe.status,
            ),
        )
        edges.append(_edge(recipe_node, f"analysis:{recipe.analysis_id}", "implements_analysis"))
        for table_name in recipe.required_tables:
            table_node = f"table:{slug(table_name)}"
            add_node(_node(table_node, table_name, "table"))
            edges.append(_edge(recipe_node, table_node, "requires_table"))
        for table_name in recipe.output_tables:
            table_node = f"table:{slug(table_name)}"
            add_node(_node(table_node, table_name, "table"))
            edges.append(_edge(recipe_node, table_node, "produces_table"))

    for ontology in ontologies:
        ontology_node = f"ontology:{ontology.id}"
        domain_node = f"domain:{slug(ontology.domain)}"
        add_node(
            _node(
                ontology_node,
                ontology.name,
                "ontology",
                licence_risk=ontology.licence_risk,
            ),
        )
        add_node(_node(domain_node, ontology.domain, "domain"))
        edges.append(_edge(ontology_node, domain_node, "maps_domain"))

    for concept in ontology_concepts or []:
        concept_node = f"concept:{concept.terminology_id}:{concept.code}"
        ontology_node = f"ontology:{concept.terminology_id}"
        domain_node = f"domain:{slug(concept.domain)}"
        add_node(
            _node(
                concept_node,
                concept.label,
                "ontology_concept",
                terminology_id=concept.terminology_id,
                concept_class=concept.concept_class,
                licence_scope=concept.licence_scope,
            ),
        )
        add_node(_node(domain_node, concept.domain, "domain"))
        edges.extend((
            _edge(concept_node, ontology_node, "concept_in_ontology"),
            _edge(concept_node, domain_node, "concept_domain"),
        ))

    for template in ontology_mapping_templates or []:
        left = f"concept:{template.left_terminology_id}:{template.left_code}"
        right = f"concept:{template.right_terminology_id}:{template.right_code}"
        edges.append(_edge(left, right, f"mapping_{template.relationship}"))

    for track in conductor_tracks or []:
        track_node = f"track:{track.id}"
        add_node(
            _node(
                track_node,
                track.title,
                "conductor_track",
                phase=track.phase,
                workstream=track.workstream,
                priority=track.priority,
            ),
        )
        for dependency in track.depends_on:
            edges.append(_edge(track_node, f"track:{dependency}", "depends_on_track"))

    for function in roadmap_functions or []:
        function_node = f"function:{function.id}"
        add_node(
            _node(
                function_node,
                function.name,
                "roadmap_function",
                interface=function.interface,
                status=function.status,
                priority=function.priority,
            ),
        )
        edges.append(_edge(function_node, f"track:{function.track_id}", "implements_track"))

    for dataset in dataset_candidates or []:
        dataset_node = f"dataset:{dataset.id}"
        jurisdiction_node = f"jurisdiction:{slug(dataset.jurisdiction)}"
        domain_node = f"domain:{slug(dataset.domain)}"
        add_node(
            _node(
                dataset_node,
                dataset.name,
                "dataset_candidate",
                priority=dataset.priority,
                access_mode=dataset.access_mode,
                licence_gate=dataset.licence_gate,
            ),
        )
        add_node(_node(jurisdiction_node, dataset.jurisdiction, "jurisdiction"))
        add_node(_node(domain_node, dataset.domain, "domain"))
        edges.extend((
            _edge(dataset_node, jurisdiction_node, "in_jurisdiction"),
            _edge(dataset_node, domain_node, "covers_domain"),
        ))

    for mapping in mapping_resources or []:
        mapping_node = f"mapping_resource:{mapping.id}"
        domain_node = f"domain:{slug(mapping.domain)}"
        add_node(
            _node(
                mapping_node,
                mapping.name,
                "mapping_resource",
                priority=mapping.priority,
                licence_gate=mapping.licence_gate,
                access_mode=mapping.access_mode,
            ),
        )
        add_node(_node(domain_node, mapping.domain, "domain"))
        edges.append(_edge(mapping_node, domain_node, "maps_domain"))

    for question in research_questions or []:
        question_node = f"research_question:{question.id}"
        add_node(
            _node(
                question_node,
                question.question,
                "research_question",
                preregistration_status=question.preregistration_status,
                osf_component=question.osf_component,
            ),
        )
        edges.append(_edge(question_node, f"track:{question.track_id}", "belongs_to_track"))
        for dataset_id in question.required_datasets:
            edges.append(
                _edge(question_node, f"dataset:{dataset_id}", "requires_dataset_candidate")
            )

    for output in output_plans or []:
        output_node = f"output:{output.id}"
        add_node(
            _node(
                output_node,
                output.path,
                "output_plan",
                output_type=output.output_type,
                target_platform=output.target_platform,
                status=output.status,
            ),
        )
        edges.append(_edge(output_node, f"track:{output.track_id}", "publishes_track"))

    return GraphTables(nodes=sorted(nodes_by_id.values(), key=itemgetter("id")), edges=edges)


def write_graph_csvs(graph: GraphTables, output_dir: Path) -> tuple[Path, Path]:
    """Write graph nodes and edges as CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    nodes_path = output_dir / "graph_nodes.csv"
    edges_path = output_dir / "graph_edges.csv"

    node_fields = sorted({field for row in graph.nodes for field in row})
    edge_fields = ["source", "target", "relationship"]
    with nodes_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=node_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(graph.nodes)
    with edges_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=edge_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(graph.edges)
    return nodes_path, edges_path

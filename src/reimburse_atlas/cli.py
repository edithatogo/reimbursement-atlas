"""Command line interface for the reimbursement atlas."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from reimburse_atlas.analysis import analysis_readiness_rows, source_readiness_rows
from reimburse_atlas.graph import build_seed_graph, write_graph_csvs
from reimburse_atlas.ingest import (
    build_first_wave_ingestion_plan,
)
from reimburse_atlas.ingest import (
    write_ingestion_plan as write_task_ingestion_plan,
)
from reimburse_atlas.ingestion import (
    assess_ingestion_readiness,
    build_first_wave_plans,
    write_ingestion_readiness,
)
from reimburse_atlas.ingestion import (
    write_ingestion_plan as write_acquisition_plan,
)
from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.licensing import evaluate_licence_gates
from reimburse_atlas.parsers import (
    parse_cms_asp_csv,
    parse_cms_clfs_csv,
    parse_cms_pfs_csv,
    parse_mbs_xml,
    parse_nhs_genomic_directory_csv,
    parse_pbs_csv,
)
from reimburse_atlas.policy_metrics import summarise_transparency
from reimburse_atlas.publication import build_publication_manifest, write_publication_manifest
from reimburse_atlas.quality import (
    access_tier_counts,
    duplicate_source_ids,
    missing_analysis_sources,
    missing_source_version_sources,
)
from reimburse_atlas.registry import (
    load_analysis_catalogue,
    load_analysis_recipes,
    load_ontology_concepts,
    load_ontology_mapping_templates,
    load_ontology_registry,
    load_source_registry,
    load_source_status,
    load_source_versions,
    project_root,
    source_ids,
)
from reimburse_atlas.review_queue import build_crosswalk_review_queue, review_rows
from reimburse_atlas.scoring import score_sources
from reimburse_atlas.validation import all_seed_pairs_ok, seed_pair_statuses

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


@app.command()
def sources(domain: Annotated[str | None, typer.Option(help="Filter by domain.")] = None) -> None:
    """Show registered reimbursement schedule sources."""
    records = load_source_registry()
    if domain is not None:
        records = [record for record in records if record.domain == domain]
    table = Table(title="Source registry")
    for column in ("id", "jurisdiction", "schedule", "domain", "access"):
        table.add_column(column)
    for record in records:
        table.add_row(
            record.id,
            record.jurisdiction,
            record.schedule,
            record.domain,
            record.access_tier,
        )
    console.print(table)


@app.command("source-status")
def source_status() -> None:
    """Show current source-status observations and next acquisition actions."""
    table = Table(title="Source status")
    for column in ("source_id", "status", "priority", "recommended_action"):
        table.add_column(column)
    for record in sorted(
        load_source_status(),
        key=lambda item: (item.retrieval_priority, item.source_id),
    ):
        table.add_row(
            record.source_id,
            record.status_label,
            str(record.retrieval_priority),
            record.recommended_action,
        )
    console.print(table)


@app.command()
def analyses() -> None:
    """Show planned analyses."""
    table = Table(title="Analysis catalogue")
    for column in ("id", "difficulty", "stage", "title"):
        table.add_column(column)
    for record in load_analysis_catalogue():
        table.add_row(record.id, record.difficulty, record.stage, record.title)
    console.print(table)


@app.command("score-sources")
def score_sources_command(
    limit: Annotated[int, typer.Option(help="Number of rows to show.")] = 20,
) -> None:
    """Score public-source readiness for reproducible analysis."""
    table = Table(title="Source readiness scores")
    for column in ("id", "score", "grade"):
        table.add_column(column)
    for score in score_sources(load_source_registry())[:limit]:
        table.add_row(score.source_id, str(score.score), score.grade)
    console.print(table)


@app.command("readiness")
def readiness(
    output_dir: Annotated[
        Path,
        typer.Argument(help="Directory for source_readiness and analysis_readiness files."),
    ] = (project_root() / "data" / "seed"),
) -> None:
    """Write source and analysis readiness tables."""
    source_rows = source_readiness_rows(load_source_registry())
    analysis_rows = analysis_readiness_rows(load_analysis_catalogue(), load_source_registry())
    write_jsonl(source_rows, output_dir / "source_readiness.jsonl")
    write_csv(source_rows, output_dir / "source_readiness.csv")
    write_jsonl(analysis_rows, output_dir / "analysis_readiness.jsonl")
    write_csv(analysis_rows, output_dir / "analysis_readiness.csv")
    console.print_json(
        json.dumps(
            {"source_rows": len(source_rows), "analysis_rows": len(analysis_rows)},
            indent=2,
        )
    )


@app.command("ingestion-plan")
def ingestion_plan(
    output_dir: Annotated[
        Path,
        typer.Argument(help="Directory for first-wave ingestion-plan files."),
    ] = (project_root() / "data" / "seed"),
) -> None:
    """Write first-wave ingestion-plan tables without fetching live data."""
    tasks = build_first_wave_ingestion_plan(load_source_registry(), load_source_versions())
    jsonl_path, csv_path = write_task_ingestion_plan(tasks, output_dir)
    console.print_json(
        json.dumps(
            {
                "task_count": len(tasks),
                "jsonl_path": str(jsonl_path),
                "csv_path": str(csv_path),
            },
            indent=2,
        )
    )


@app.command("acquisition-plan")
def acquisition_plan(
    output_dir: Annotated[
        Path,
        typer.Argument(help="Directory for acquisition plan and readiness artifacts."),
    ] = (project_root() / "data" / "seed"),
) -> None:
    """Write licence-gated acquisition plans for first-wave source versions."""
    plans = build_first_wave_plans(load_source_registry(), load_source_versions())
    readiness_records = assess_ingestion_readiness(plans)
    plan_csv, plan_jsonl = write_acquisition_plan(plans, output_dir)
    readiness_csv, readiness_jsonl = write_ingestion_readiness(readiness_records, output_dir)
    console.print_json(
        json.dumps(
            {
                "plan_count": len(plans),
                "readiness_count": len(readiness_records),
                "plan_csv": str(plan_csv),
                "plan_jsonl": str(plan_jsonl),
                "readiness_csv": str(readiness_csv),
                "readiness_jsonl": str(readiness_jsonl),
            },
            indent=2,
        )
    )


@app.command("license-gates")
def license_gates() -> None:
    """Show cautious raw-data publication gates for all registered sources."""
    table = Table(title="Licence and redistribution gates")
    for column in ("source_id", "status", "public_dataset_policy"):
        table.add_column(column)
    for gate in evaluate_licence_gates(load_source_registry()):
        table.add_row(gate.source_id, gate.status, gate.public_dataset_policy)
    console.print(table)


@app.command("policy-summary")
def policy_summary() -> None:
    """Print source transparency metrics useful for policy framing."""
    summary = summarise_transparency(load_source_registry())
    console.print_json(json.dumps(asdict(summary), indent=2))


@app.command("seed-lake")
def seed_lake(
    output_dir: Annotated[
        Path,
        typer.Argument(help="Output directory for seed-lake artifacts."),
    ] = (project_root() / "data" / "derived" / "seed_lake"),
) -> None:
    """Materialise local seed registries into a JSONL/CSV lake layout."""
    from reimburse_atlas.datalake import materialise_seed_lake

    manifest = materialise_seed_lake(output_dir)
    console.print_json(json.dumps(asdict(manifest), indent=2))


@app.command("source-snapshots")
def source_snapshots(
    output_dir: Annotated[
        Path,
        typer.Argument(help="Output directory for source snapshot records."),
    ] = (project_root() / "data" / "derived" / "snapshots"),
) -> None:
    """Write checksum/provenance records for committed synthetic fixtures."""
    from reimburse_atlas.snapshots import build_fixture_snapshots, write_snapshot_records

    records = build_fixture_snapshots()
    jsonl_path, csv_path = write_snapshot_records(records, output_dir)
    console.print_json(
        json.dumps(
            {
                "snapshot_count": len(records),
                "jsonl_path": str(jsonl_path),
                "csv_path": str(csv_path),
            },
            indent=2,
        )
    )


@app.command("snapshot-local-file")
def snapshot_local_file_command(
    source_version_id: Annotated[str, typer.Option(help="Registered source version id.")],
    path: Annotated[Path, typer.Argument(help="Manually downloaded local source file.")],
    content_type: Annotated[
        str,
        typer.Option(help="MIME-ish content type."),
    ] = "application/octet-stream",
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory where snapshot metadata will be written."),
    ] = (project_root() / "data" / "derived" / "reviewed_snapshots"),
) -> None:
    """Create checksum/provenance metadata for a reviewed local source file."""
    from reimburse_atlas.local_sources import snapshot_reviewed_local_file
    from reimburse_atlas.snapshots import write_snapshot_records

    record = snapshot_reviewed_local_file(
        source_version_id=source_version_id,
        path=path,
        content_type=content_type,
        cache_scope="local_raw_only",
        notes="Reviewed local raw snapshot generated by CLI; raw file remains outside git.",
    )
    jsonl_path, csv_path = write_snapshot_records([record], output_dir)
    console.print_json(
        json.dumps(
            {
                "snapshot_id": record.id,
                "source_id": record.source_id,
                "checksum_sha256": record.checksum_sha256,
                "jsonl_path": str(jsonl_path),
                "csv_path": str(csv_path),
            },
            indent=2,
        )
    )


@app.command("parse-local-source")
def parse_local_source_command(
    source_version_id: Annotated[str, typer.Option(help="Registered source version id.")],
    path: Annotated[Path, typer.Argument(help="Reviewed local source file to parse.")],
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for derived normalised rows."),
    ] = (project_root() / "data" / "derived" / "reviewed_sources"),
) -> None:
    """Parse a reviewed local source file into derived schedule/coverage rows."""
    from reimburse_atlas.local_sources import parse_reviewed_local_file

    result = parse_reviewed_local_file(
        source_version_id=source_version_id,
        path=path,
        output_dir=output_dir,
    )
    console.print_json(json.dumps({**asdict(result)}, default=str, indent=2))


@app.command("vertical-slice")
def vertical_slice(
    output_dir: Annotated[
        Path,
        typer.Argument(help="Directory for parsed fixture-derived artefacts."),
    ] = (project_root() / "data" / "derived" / "vertical_slice"),
) -> None:
    """Parse local first-wave fixtures into normalised contracts."""
    from reimburse_atlas.analysis import (
        build_crosswalk_candidates,
        median_payment_by_source,
        policy_signal_matrix,
        priced_share,
    )
    from reimburse_atlas.io import pydantic_rows

    fixtures = project_root() / "tests" / "fixtures"
    mbs_records = parse_mbs_xml(fixtures / "mbs_fragment.xml")
    pbs_records = parse_pbs_csv(fixtures / "pbs_fixture.csv")
    clfs_records = parse_cms_clfs_csv(fixtures / "cms_clfs_fixture.csv")
    pfs_records = parse_cms_pfs_csv(fixtures / "cms_pfs_fixture.csv")
    asp_records = parse_cms_asp_csv(fixtures / "cms_asp_fixture.csv")
    coverage_records = parse_nhs_genomic_directory_csv(
        fixtures / "nhs_genomic_directory_fixture.csv"
    )
    schedule_records = [*mbs_records, *pbs_records, *clfs_records, *pfs_records, *asp_records]
    crosswalks = build_crosswalk_candidates(mbs_records, clfs_records, threshold=0.05)
    review_queue = build_crosswalk_review_queue(crosswalks)
    payment_rows = median_payment_by_source(schedule_records)
    priced_rows = [
        {"source_id": source_id, "priced_share": share}
        for source_id, share in priced_share(schedule_records).items()
    ]
    signal_rows = policy_signal_matrix(schedule_records, coverage_records)
    write_jsonl(pydantic_rows(schedule_records), output_dir / "schedule_items.jsonl")
    write_csv(pydantic_rows(schedule_records), output_dir / "schedule_items.csv")
    write_jsonl(pydantic_rows(coverage_records), output_dir / "coverage_decisions.jsonl")
    write_csv(pydantic_rows(coverage_records), output_dir / "coverage_decisions.csv")
    write_jsonl(pydantic_rows(crosswalks), output_dir / "crosswalk_candidates.jsonl")
    write_csv(pydantic_rows(crosswalks), output_dir / "crosswalk_candidates.csv")
    write_jsonl(review_rows(review_queue), output_dir / "crosswalk_review_queue.jsonl")
    write_csv(review_rows(review_queue), output_dir / "crosswalk_review_queue.csv")
    write_jsonl(payment_rows, output_dir / "median_payment_by_source.jsonl")
    write_csv(payment_rows, output_dir / "median_payment_by_source.csv")
    write_jsonl(priced_rows, output_dir / "priced_share.jsonl")
    write_csv(priced_rows, output_dir / "priced_share.csv")
    write_jsonl(signal_rows, output_dir / "policy_signal_matrix.jsonl")
    write_csv(signal_rows, output_dir / "policy_signal_matrix.csv")
    console.print_json(
        json.dumps(
            {
                "schedule_items": len(schedule_records),
                "coverage_decisions": len(coverage_records),
                "crosswalk_candidates": len(crosswalks),
                "crosswalk_review_rows": len(review_queue),
                "policy_signal_rows": len(signal_rows),
                "output_dir": str(output_dir),
            },
            indent=2,
        )
    )


@app.command("export-graph")
def export_graph(
    output_dir: Annotated[
        Path,
        typer.Argument(help="Directory for graph_nodes.csv and graph_edges.csv"),
    ] = (project_root() / "data" / "seed"),
) -> None:
    """Export the seed source-analysis-ontology graph."""
    graph = build_seed_graph(
        load_source_registry(),
        load_analysis_catalogue(),
        load_ontology_registry(),
        load_source_versions(),
        load_analysis_recipes(),
        load_ontology_concepts(),
        load_ontology_mapping_templates(),
    )
    nodes_path, edges_path = write_graph_csvs(graph, output_dir)
    console.print_json(
        json.dumps(
            {
                "nodes": len(graph.nodes),
                "edges": len(graph.edges),
                "nodes_path": str(nodes_path),
                "edges_path": str(edges_path),
            },
            indent=2,
        )
    )


@app.command()
def validate() -> None:
    """Validate seed registries and source references."""
    sources_ = load_source_registry()
    analyses_ = load_analysis_catalogue()
    ontologies_ = load_ontology_registry()
    versions_ = load_source_versions()
    status_ = load_source_status()
    ids_ = source_ids(sources_)
    missing = missing_analysis_sources(analyses_, ids_)
    missing_versions = missing_source_version_sources(versions_, ids_)
    duplicates = duplicate_source_ids(sources_)
    missing_status_sources = sorted({record.source_id for record in status_} - ids_)
    payload = {
        "source_count": len(sources_),
        "analysis_count": len(analyses_),
        "ontology_count": len(ontologies_),
        "source_version_count": len(versions_),
        "source_status_count": len(status_),
        "access_tier_counts": access_tier_counts(sources_),
        "duplicate_source_ids": duplicates,
        "missing_analysis_sources": missing,
        "missing_source_version_sources": missing_versions,
        "missing_status_sources": missing_status_sources,
    }
    console.print_json(json.dumps(payload, indent=2))
    if missing or missing_versions or missing_status_sources or duplicates:
        raise typer.Exit(code=1)


@app.command("validate-seed-files")
def validate_seed_files() -> None:
    """Validate that JSONL seed tables and their CSV mirrors are in sync."""
    statuses = seed_pair_statuses()
    table = Table(title="Seed JSONL/CSV sync")
    for column in ("table", "jsonl_rows", "csv_rows", "ok", "missing_in_csv", "missing_in_jsonl"):
        table.add_column(column)
    for status in statuses:
        table.add_row(
            status.table_name,
            str(status.jsonl_rows),
            str(status.csv_rows),
            str(status.ok),
            ",".join(status.missing_in_csv),
            ",".join(status.missing_in_jsonl),
        )
    console.print(table)
    if not all_seed_pairs_ok(statuses):
        raise typer.Exit(code=1)


@app.command("publication-manifest")
def publication_manifest(
    output_path: Annotated[
        Path,
        typer.Argument(help="Output path for the candidate public dataset manifest."),
    ] = (project_root() / "data" / "derived" / "publication_manifest.json"),
) -> None:
    """Write a candidate Hugging Face/public-data publication manifest."""
    manifest = build_publication_manifest()
    path = write_publication_manifest(manifest, output_path)
    console.print_json(
        json.dumps(
            {
                "artifact_count": manifest.artifact_count,
                "warning_count": len(manifest.warnings),
                "output_path": str(path),
            },
            indent=2,
        )
    )


@app.command("reviewed-source-bundle")
def reviewed_source_bundle_command(
    source_version_id: Annotated[str, typer.Option(help="Registered source version id.")],
    path: Annotated[Path, typer.Argument(help="Reviewed local source file to snapshot and parse.")],
    content_type: Annotated[
        str,
        typer.Option(help="MIME-ish content type."),
    ] = "application/octet-stream",
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for reviewed-source bundles."),
    ] = (project_root() / "data" / "derived" / "reviewed_source_bundles"),
) -> None:
    """Build a derived-only reviewed source package from one local file."""
    from reimburse_atlas.local_sources import build_reviewed_source_bundle

    result = build_reviewed_source_bundle(
        source_version_id=source_version_id,
        path=path,
        content_type=content_type,
        output_dir=output_dir,
    )
    console.print_json(json.dumps({**asdict(result)}, default=str, indent=2))


@app.command("ontology-seed")
def ontology_seed(
    output_dir: Annotated[
        Path,
        typer.Argument(help="Directory for ontology concept and mapping-template seeds."),
    ] = (project_root() / "data" / "seed"),
) -> None:
    """Generate local-only ontology concept and mapping-template seed files."""
    from reimburse_atlas.terminologies import build_mapping_templates, parse_ontology_concepts_csv

    fixture = project_root() / "tests" / "fixtures" / "ontology_concepts_fixture.csv"
    concepts = parse_ontology_concepts_csv(fixture)
    templates = build_mapping_templates(concepts)
    concept_rows = [concept.model_dump(mode="json") for concept in concepts]
    write_jsonl(concept_rows, output_dir / "ontology_concepts.jsonl")
    write_csv(concept_rows, output_dir / "ontology_concepts.csv")
    write_jsonl(
        [template.model_dump(mode="json") for template in templates],
        output_dir / "ontology_mapping_templates.jsonl",
    )
    write_csv(
        [template.model_dump(mode="json") for template in templates],
        output_dir / "ontology_mapping_templates.csv",
    )
    console.print_json(
        json.dumps(
            {
                "concept_count": len(concepts),
                "mapping_template_count": len(templates),
                "output_dir": str(output_dir),
            },
            indent=2,
        )
    )


@app.command()
def snapshot() -> None:
    """Print a concise project snapshot for future agents or maintainers."""
    sources_ = load_source_registry()
    analyses_ = load_analysis_catalogue()
    ontologies_ = load_ontology_registry()
    versions_ = load_source_versions()
    status_ = load_source_status()
    tasks = build_first_wave_ingestion_plan(sources_, versions_)
    ready_analyses = [
        row
        for row in analysis_readiness_rows(analyses_, sources_)
        if bool(row["ready_for_prototype"])
    ]
    payload = {
        "project": "reimbursement-atlas-conductor",
        "conductor_context": str(project_root() / "conductor"),
        "source_count": len(sources_),
        "analysis_count": len(analyses_),
        "ontology_count": len(ontologies_),
        "source_version_count": len(versions_),
        "source_status_count": len(status_),
        "ingestion_task_count": len(tasks),
        "prototype_ready_analysis_count": len(ready_analyses),
        "top_source_scores": [asdict(score) for score in score_sources(sources_)[:5]],
        "next_vertical_slice": "MBS XML + CMS CLFS + NHS genomic directory + reviewable crosswalks",
    }
    console.print_json(json.dumps(payload, indent=2))


@app.command()
def export_schema(output_dir: Annotated[Path, typer.Argument()] = Path("schema")) -> None:
    """Export JSON schemas for registries and derived contracts."""
    from reimburse_atlas.adapters import SourceAcquisitionPlan
    from reimburse_atlas.contracts import (
        CoverageDecisionRecord,
        CrosswalkCandidate,
        ProvenanceRecord,
        ScheduleItemRecord,
        SourceSnapshotRecord,
    )
    from reimburse_atlas.ingest import IngestionTaskRecord
    from reimburse_atlas.models import (
        AnalysisRecipeRecord,
        AnalysisRecord,
        OntologyRecord,
        SourceRecord,
        SourceStatusRecord,
        SourceVersionRecord,
    )
    from reimburse_atlas.terminologies import OntologyConceptRecord, OntologyMappingTemplate

    output_dir.mkdir(parents=True, exist_ok=True)
    models = (
        SourceRecord,
        SourceStatusRecord,
        AnalysisRecord,
        AnalysisRecipeRecord,
        OntologyRecord,
        SourceVersionRecord,
        ProvenanceRecord,
        ScheduleItemRecord,
        SourceSnapshotRecord,
        CoverageDecisionRecord,
        CrosswalkCandidate,
        IngestionTaskRecord,
        SourceAcquisitionPlan,
        OntologyConceptRecord,
        OntologyMappingTemplate,
    )
    for model in models:
        path = output_dir / f"{model.__name__}.schema.json"
        path.write_text(json.dumps(model.model_json_schema(), indent=2) + "\n", encoding="utf-8")
        console.print(f"Wrote {path}")


if __name__ == "__main__":
    app()

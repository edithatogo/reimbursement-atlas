"""Command line interface for the reimbursement atlas."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Annotated, cast

import typer
from rich.console import Console
from rich.table import Table

from reimburse_atlas.acquisition_pack import (
    acquisition_pack_summary,
    build_manual_acquisition_steps,
    write_manual_acquisition_pack,
)
from reimburse_atlas.analysis import analysis_readiness_rows, source_readiness_rows
from reimburse_atlas.automation import (
    automation_control_records,
    scan_workflow_uses,
    workflow_policy_records,
    workflow_policy_summary,
)
from reimburse_atlas.data_dictionary import build_data_dictionary, write_data_dictionary
from reimburse_atlas.evidence_readiness import build_evidence_readiness, write_evidence_readiness
from reimburse_atlas.final_handoff import build_final_handoff_tasks, write_final_handoff_tasks
from reimburse_atlas.github_project import build_github_project_items, write_github_project_items
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
from reimburse_atlas.io import pydantic_rows, write_csv, write_jsonl
from reimburse_atlas.licensing import evaluate_licence_gates
from reimburse_atlas.local_quality import (
    QualityGateProfile,
    run_quality_gate_profile,
    write_quality_gate_run,
)
from reimburse_atlas.osf_registration import check_registration_drift
from reimburse_atlas.osf_sync import OsfRemoteRecord, reconcile_osf_manifest
from reimburse_atlas.parsers import (
    parse_cms_asp_csv,
    parse_cms_clfs_csv,
    parse_cms_pfs_csv,
    parse_mbs_txt_pair,
    parse_mbs_xml,
    parse_nhs_genomic_directory_csv,
    parse_pbs_csv,
)
from reimburse_atlas.policy_metrics import summarise_transparency
from reimburse_atlas.protocols import build_protocol_status, write_protocol_status
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
    load_conductor_tracks,
    load_dataset_candidates,
    load_mapping_resources,
    load_ontology_concepts,
    load_ontology_mapping_templates,
    load_ontology_registry,
    load_output_artifact_plans,
    load_research_questions,
    load_roadmap_functions,
    load_runtime_targets,
    load_source_files,
    load_source_registry,
    load_source_status,
    load_source_versions,
    project_root,
    repo_relative,
    source_ids,
)
from reimburse_atlas.review_queue import build_crosswalk_review_queue, review_rows
from reimburse_atlas.sbom import build_dashboard_sbom, build_python_sbom, sbom_summary, write_sbom
from reimburse_atlas.scoring import score_sources
from reimburse_atlas.source_contracts import (
    build_source_contract_validations,
    write_mbs_pair_contract_evidence,
    write_source_contract_validations,
)
from reimburse_atlas.source_drift import (
    build_default_source_drift_report,
    compare_tabular_files,
    write_source_drift_report,
)
from reimburse_atlas.validation import all_seed_pairs_ok, seed_pair_statuses
from reimburse_atlas.vector_index import (
    VectorIndexDependencyError,
    build_lancedb_index,
    schedule_item_vector_rows,
    write_arrow_vector_seed,
)

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


@app.command("runtime-targets")
def runtime_targets() -> None:
    """Show language and toolchain runtime targets including Mojo and Python 3.14."""
    table = Table(title="Runtime targets")
    for column in ("id", "name", "target", "installation_status", "local_status"):
        table.add_column(column)
    for record in load_runtime_targets():
        table.add_row(
            record.id,
            record.name,
            record.version_target,
            record.installation_status,
            record.local_status,
        )
    console.print(table)


@app.command("roadmap")
def roadmap() -> None:
    """Show Conductor tracks and planned functions."""
    tracks = {track.id: track for track in load_conductor_tracks()}
    table = Table(title="Conductor roadmap tracks")
    for column in ("track", "priority", "phase", "functions"):
        table.add_column(column)
    functions = load_roadmap_functions()
    for track in tracks.values():
        function_count = sum(1 for function in functions if function.track_id == track.id)
        table.add_row(track.title, track.priority, track.phase, str(function_count))
    console.print(table)


@app.command("source-download-plan")
def source_download_plan(
    attempt: Annotated[
        bool,
        typer.Option(help="Attempt executable curl/wget downloads into ignored local raw storage."),
    ] = False,
    resume_downloads: Annotated[
        bool,
        typer.Option(help="Allow curl/wget resume flags for sources that support byte ranges."),
    ] = False,
    method: Annotated[str, typer.Option(help="Download method: curl or wget.")] = "curl",
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for download plans and attempt records."),
    ] = (project_root() / "data" / "derived" / "source_downloads"),
) -> None:
    """Generate curl/wget/API source acquisition plans and optional attempts."""
    if method not in {"curl", "wget"}:
        msg = "method must be curl or wget"
        raise typer.BadParameter(msg)
    from reimburse_atlas.source_downloads import (
        attempt_download,
        build_download_plan,
        write_download_outputs,
    )

    records = load_source_files()
    plans = [
        build_download_plan(record, preferred_method=method, resume_downloads=resume_downloads)
        for record in records
    ]
    attempts = (
        [
            attempt_download(
                record,
                preferred_method=method,
                resume_downloads=resume_downloads,
            )
            for record in records
        ]
        if attempt
        else []
    )
    paths = write_download_outputs(plans, attempts, output_dir=output_dir)
    console.print_json(
        json.dumps(
            {
                "plans": len(plans),
                "attempts": len(attempts),
                "downloaded": sum(1 for record in attempts if record.status == "downloaded"),
                "blocked_network": sum(
                    1 for record in attempts if record.status == "blocked_network"
                ),
                "skipped_licence_gate": sum(
                    1 for record in attempts if record.status == "skipped_licence_gate"
                ),
                "paths": [repo_relative(path) for path in paths],
            },
            indent=2,
        )
    )


@app.command("research-map")
def research_map() -> None:
    """Show research questions, dataset candidates, mapping resources and output plans."""
    payload = {
        "conductor_tracks": len(load_conductor_tracks()),
        "roadmap_functions": len(load_roadmap_functions()),
        "dataset_candidates": len(load_dataset_candidates()),
        "mapping_resources": len(load_mapping_resources()),
        "research_questions": len(load_research_questions()),
        "output_artifact_plans": len(load_output_artifact_plans()),
        "runtime_targets": len(load_runtime_targets()),
    }
    console.print_json(json.dumps(payload, indent=2))


@app.command("protocol-status")
def protocol_status(
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for generated protocol status artefacts."),
    ] = (project_root() / "data" / "derived" / "protocols"),
) -> None:
    """Generate OSF-aligned protocol/report completeness status records."""
    rows = build_protocol_status(load_research_questions())
    paths = write_protocol_status(rows, output_dir=output_dir)
    console.print_json(
        json.dumps(
            {
                "protocols": len(rows),
                "osf_ready": sum(1 for row in rows if row.osf_ready),
                "average_completeness": round(
                    sum(row.completeness_score for row in rows) / len(rows), 4
                )
                if rows
                else 0.0,
                "paths": [repo_relative(path) for path in paths],
            },
            indent=2,
        )
    )


@app.command("source-validation")
def source_validation(
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for source-content validation artefacts."),
    ] = (project_root() / "data" / "derived" / "source_validation"),
) -> None:
    """Validate locally downloaded source files without exposing raw payloads."""
    from reimburse_atlas.source_validation import (
        build_source_content_validations,
        write_source_content_validations,
    )

    rows = build_source_content_validations(load_source_files())
    paths = write_source_content_validations(rows, output_dir=output_dir)
    console.print_json(
        json.dumps(
            {
                "validation_count": len(rows),
                "pass": sum(row.validation_status == "pass" for row in rows),
                "missing": sum(row.validation_status == "missing" for row in rows),
                "skipped": sum(row.validation_status == "skipped" for row in rows),
                "paths": [repo_relative(path) for path in paths],
            },
            indent=2,
        )
    )


@app.command("source-contracts")
def source_contracts(
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for source-specific contract-validation artefacts."),
    ] = (project_root() / "data" / "derived" / "source_contracts"),
) -> None:
    """Validate source-specific local-file contracts before bundle parsing."""
    rows = build_source_contract_validations(load_source_files())
    paths = write_source_contract_validations(rows, output_dir=output_dir)
    console.print_json(
        json.dumps(
            {
                "contract_count": len(rows),
                "pass": sum(row.contract_status == "pass" for row in rows),
                "missing": sum(row.contract_status == "missing" for row in rows),
                "skipped": sum(row.contract_status == "skipped" for row in rows),
                "fail": sum(row.contract_status == "fail" for row in rows),
                "paths": [repo_relative(path) for path in paths],
            },
            indent=2,
        )
    )


@app.command("github-project-export")
def github_project_export(
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for generated GitHub Project import artefacts."),
    ] = (project_root() / "data" / "derived" / "github_project"),
) -> None:
    """Generate GitHub Project issue/track import rows from Conductor context."""
    rows = build_github_project_items(load_conductor_tracks())
    paths = write_github_project_items(rows, output_dir=output_dir)
    console.print_json(
        json.dumps(
            {
                "project_items": len(rows),
                "issues": sum(row.item_type == "issue" for row in rows),
                "tracks": sum(row.item_type == "track" for row in rows),
                "paths": [repo_relative(path) for path in paths],
            },
            indent=2,
        )
    )


@app.command("final-handoff")
def final_handoff(
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for final handoff checklist artefacts."),
    ] = (project_root() / "data" / "derived" / "final_handoff"),
) -> None:
    """Generate the final environment-dependent handoff checklist."""
    rows = build_final_handoff_tasks()
    paths = write_final_handoff_tasks(rows, output_dir=output_dir)
    console.print_json(
        json.dumps(
            {
                "tasks": len(rows),
                "ready_local": sum(row.status == "ready_local" for row in rows),
                "blocked_network": sum(row.status == "blocked_network" for row in rows),
                "blocked_secret": sum(row.status == "blocked_secret" for row in rows),
                "blocked_review": sum(row.status == "blocked_review" for row in rows),
                "paths": [repo_relative(path) for path in paths],
            },
            indent=2,
        )
    )


@app.command("data-quality")
def data_quality(
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for generated data-quality artefacts."),
    ] = (project_root() / "data" / "derived" / "data_quality"),
) -> None:
    """Generate table-level data quality checks for release review."""
    from reimburse_atlas.data_quality import build_data_quality_checks, write_data_quality_checks

    rows = build_data_quality_checks()
    paths = write_data_quality_checks(rows, output_dir=output_dir)
    blocking = sum(row.severity == "blocking" and row.status in {"fail", "missing"} for row in rows)
    console.print_json(
        json.dumps(
            {
                "check_count": len(rows),
                "blocking_failures": blocking,
                "paths": [repo_relative(path) for path in paths],
            },
            indent=2,
        )
    )


@app.command("roadmap-linkages")
def roadmap_linkages(
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for generated roadmap linkage artefacts."),
    ] = (project_root() / "data" / "derived" / "roadmap_linkages"),
) -> None:
    """Generate research-question linkages to datasets, mappings and outputs."""
    from reimburse_atlas.roadmap_linkages import build_research_linkages, write_research_linkages

    rows = build_research_linkages(
        research_questions=load_research_questions(),
        sources=load_source_registry(),
        dataset_candidates=load_dataset_candidates(),
        mapping_resources=load_mapping_resources(),
        output_plans=load_output_artifact_plans(),
    )
    jsonl_path, csv_path = write_research_linkages(rows, output_dir=output_dir)
    console.print_json(
        json.dumps(
            {
                "linkage_count": len(rows),
                "missing": sum(row.readiness_status == "missing" for row in rows),
                "jsonl_path": str(jsonl_path),
                "csv_path": str(csv_path),
            },
            indent=2,
        )
    )


@app.command("data-dictionary")
def data_dictionary(
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for generated data-dictionary artefacts."),
    ] = (project_root() / "data" / "derived" / "data_dictionary"),
) -> None:
    """Generate a dashboard-safe data dictionary for public candidate artefacts."""
    rows = build_data_dictionary()
    paths = write_data_dictionary(rows, output_dir=output_dir)
    console.print_json(
        json.dumps(
            {
                "table_count": len(rows),
                "total_rows_documented": sum(row.row_count for row in rows),
                "paths": [repo_relative(path) for path in paths],
            },
            indent=2,
        )
    )


@app.command("evidence-readiness")
def evidence_readiness(
    output_dir: Annotated[
        Path,
        typer.Option(
            help="Directory for generated research-question evidence-readiness artefacts."
        ),
    ] = (project_root() / "data" / "derived" / "evidence_readiness"),
) -> None:
    """Generate evidence-readiness status for protocolled research questions."""
    rows = build_evidence_readiness()
    paths = write_evidence_readiness(rows, output_dir=output_dir)
    console.print_json(
        json.dumps(
            {
                "research_questions": len(rows),
                "evidence_ready": sum(row.readiness_stage == "evidence_ready" for row in rows),
                "prototype_ready": sum(row.readiness_stage == "prototype_ready" for row in rows),
                "paths": [repo_relative(path) for path in paths],
            },
            indent=2,
        )
    )


@app.command("source-drift")
def source_drift(
    left_path: Annotated[Path | None, typer.Option(help="Optional left CSV/JSONL file.")] = None,
    right_path: Annotated[Path | None, typer.Option(help="Optional right CSV/JSONL file.")] = None,
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for generated source-drift artefacts."),
    ] = (project_root() / "data" / "derived" / "source_drift"),
) -> None:
    """Generate default or ad hoc schema/row-count drift checks."""
    if (left_path is None) != (right_path is None):
        msg = "left-path and right-path must be provided together"
        raise typer.BadParameter(msg)
    rows = (
        [compare_tabular_files(left_path, right_path)]
        if left_path is not None and right_path is not None
        else build_default_source_drift_report()
    )
    paths = write_source_drift_report(rows, output_dir=output_dir)
    console.print_json(
        json.dumps(
            {
                "drift_checks": len(rows),
                "failures": sum(row.status in {"fail", "missing"} for row in rows),
                "warnings": sum(row.status == "warn" for row in rows),
                "paths": [repo_relative(path) for path in paths],
            },
            indent=2,
        )
    )


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


@app.command("source-files")
def source_files() -> None:
    """Show exact first-wave source files, endpoints and licence gates."""
    table = Table(title="Exact source-file acquisition records")
    for column in ("id", "source_id", "mode", "licence_gate", "file_name"):
        table.add_column(column)
    for record in load_source_files():
        table.add_row(
            record.id,
            record.source_id,
            record.acquisition_mode,
            record.licence_gate,
            record.file_name,
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


@app.command("policy-demonstrators")
def policy_demonstrators(
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for policy-demonstrator artefacts."),
    ] = (project_root() / "data" / "derived" / "policy_demonstrators"),
) -> None:
    """Generate the first policy demonstrator briefs from local fixtures."""
    from reimburse_atlas.demonstrators import build_policy_demonstrator_briefs
    from reimburse_atlas.parsers import (
        parse_cms_asp_csv,
        parse_cms_clfs_csv,
        parse_cms_pfs_csv,
        parse_mbs_xml,
        parse_nhs_genomic_directory_csv,
        parse_pbs_csv,
    )

    fixtures = project_root() / "tests" / "fixtures"
    parsed_sources = {
        "au_mbs": parse_mbs_xml(fixtures / "mbs_fragment.xml"),
        "us_cms_clfs": parse_cms_clfs_csv(fixtures / "cms_clfs_fixture.csv"),
        "us_cms_pfs": parse_cms_pfs_csv(fixtures / "cms_pfs_fixture.csv"),
        "au_pbs": parse_pbs_csv(fixtures / "pbs_fixture.csv"),
        "us_cms_asp": parse_cms_asp_csv(fixtures / "cms_asp_fixture.csv"),
        "uk_genomic_test_directory": parse_nhs_genomic_directory_csv(
            fixtures / "nhs_genomic_directory_fixture.csv"
        ),
    }
    briefs = build_policy_demonstrator_briefs(parsed_sources)
    from reimburse_atlas.io import pydantic_rows, write_csv, write_jsonl

    rows = pydantic_rows(briefs)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(rows, output_dir / "policy_briefs.jsonl")
    write_csv(rows, output_dir / "policy_briefs.csv")
    (output_dir / "summary.json").write_text(
        json.dumps(
            {
                "brief_count": len(briefs),
                "source_count": len(parsed_sources),
                "brief_ids": [brief.demonstrator_id for brief in briefs],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    console.print_json(
        json.dumps(
            {
                "brief_count": len(briefs),
                "source_count": len(parsed_sources),
                "output_dir": str(output_dir),
            },
            indent=2,
        )
    )


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


@app.command("parse-mbs-txt-pair")
def parse_mbs_txt_pair_command(
    item_map_path: Annotated[Path, typer.Argument(help="Reviewed local MBS item-map TXT file.")],
    descriptor_path: Annotated[
        Path,
        typer.Argument(help="Reviewed local MBS descriptor TXT file."),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for derived normalised MBS TXT rows."),
    ] = (project_root() / "data" / "derived" / "reviewed_sources"),
) -> None:
    """Parse the current MBS item-map and descriptor TXT pair into derived rows."""
    records = parse_mbs_txt_pair(item_map_path, descriptor_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = pydantic_rows(records)
    jsonl_path = write_jsonl(rows, output_dir / "au_mbs_20260701_txt_pair_schedule_items.jsonl")
    csv_path = write_csv(rows, output_dir / "au_mbs_20260701_txt_pair_schedule_items.csv")
    console.print_json(
        json.dumps(
            {
                "record_count": len(records),
                "jsonl_path": str(jsonl_path),
                "csv_path": str(csv_path),
                "raw_files_copied": False,
            },
            indent=2,
        )
    )


@app.command("reviewed-mbs-txt-pair-bundle")
def reviewed_mbs_txt_pair_bundle_command(
    item_map_path: Annotated[Path, typer.Argument(help="Reviewed local MBS item-map TXT file.")],
    descriptor_path: Annotated[
        Path,
        typer.Argument(help="Reviewed local MBS descriptor TXT file."),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for derived-only reviewed MBS TXT-pair bundles."),
    ] = (project_root() / "data" / "derived" / "reviewed_source_bundles"),
    retrieved_at: Annotated[
        str | None,
        typer.Option(help="Optional ISO-8601 retrieval timestamp for both local files."),
    ] = None,
) -> None:
    """Create a derived-only reviewed-source bundle for an MBS TXT file pair."""
    from reimburse_atlas.local_sources import build_mbs_txt_pair_bundle

    result = build_mbs_txt_pair_bundle(
        item_map_path=item_map_path,
        descriptor_path=descriptor_path,
        output_dir=output_dir,
        retrieved_at=retrieved_at,
    )
    write_mbs_pair_contract_evidence(
        item_map_path=item_map_path,
        descriptor_path=descriptor_path,
        output_dir=result.bundle_dir,
        records=load_source_files(),
    )
    console.print_json(json.dumps(asdict(result), default=str, indent=2))


@app.command("manual-acquisition-pack")
def manual_acquisition_pack(
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for manual reviewed-source acquisition-pack files."),
    ] = (project_root() / "data" / "derived" / "manual_acquisition_pack"),
) -> None:
    """Generate a licence-aware manual acquisition checklist from source-file records."""
    steps = build_manual_acquisition_steps(load_source_files())
    jsonl_path, csv_path, readme_path, shell_path = write_manual_acquisition_pack(
        steps,
        output_dir=output_dir,
    )
    console.print_json(
        json.dumps(
            {
                **acquisition_pack_summary(steps),
                "jsonl_path": str(jsonl_path),
                "csv_path": str(csv_path),
                "readme_path": str(readme_path),
                "shell_path": str(shell_path),
            },
            indent=2,
        )
    )


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
        build_mapping_evidence_matrix,
        median_payment_by_source,
        policy_signal_matrix,
        priced_share,
    )
    from reimburse_atlas.gold_standard import (
        build_gold_standard_set,
        build_mapping_calibration_cases,
        build_mapping_calibration_summary,
        build_negative_controls,
    )

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
    mapping_rows = build_mapping_evidence_matrix(
        mbs_records,
        [*clfs_records, *pfs_records],
        threshold=0.05,
    )
    gold_standard_rows = build_gold_standard_set()
    negative_control_rows = build_negative_controls()
    calibration_cases = build_mapping_calibration_cases(crosswalks)
    calibration_summary = build_mapping_calibration_summary(calibration_cases)
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
    write_jsonl(pydantic_rows(mapping_rows), output_dir / "mapping_evidence_matrix.jsonl")
    write_csv(pydantic_rows(mapping_rows), output_dir / "mapping_evidence_matrix.csv")
    write_jsonl(pydantic_rows(gold_standard_rows), output_dir / "gold_standard_mappings.jsonl")
    write_csv(pydantic_rows(gold_standard_rows), output_dir / "gold_standard_mappings.csv")
    write_jsonl(pydantic_rows(negative_control_rows), output_dir / "negative_controls.jsonl")
    write_csv(pydantic_rows(negative_control_rows), output_dir / "negative_controls.csv")
    write_jsonl(pydantic_rows(calibration_cases), output_dir / "mapping_calibration_cases.jsonl")
    write_csv(pydantic_rows(calibration_cases), output_dir / "mapping_calibration_cases.csv")
    write_jsonl(
        [calibration_summary.model_dump(mode="json")],
        output_dir / "mapping_calibration_summary.jsonl",
    )
    write_csv(
        [calibration_summary.model_dump(mode="json")],
        output_dir / "mapping_calibration_summary.csv",
    )
    console.print_json(
        json.dumps(
            {
                "schedule_items": len(schedule_records),
                "coverage_decisions": len(coverage_records),
                "crosswalk_candidates": len(crosswalks),
                "crosswalk_review_rows": len(review_queue),
                "policy_signal_rows": len(signal_rows),
                "mapping_evidence_rows": len(mapping_rows),
                "calibration_cases": len(calibration_cases),
                "output_dir": str(output_dir),
            },
            indent=2,
        )
    )


@app.command("vector-seed")
def vector_seed(
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for local Arrow/LanceDB vector-search prototypes."),
    ] = (project_root() / "data" / "derived" / "vector_seed"),
    build_lance: Annotated[
        bool,
        typer.Option(help="Also build a local LanceDB table under the output directory."),
    ] = False,
) -> None:
    """Build deterministic lexical vector seed data for schedule-item search."""
    fixtures = project_root() / "tests" / "fixtures"
    schedule_records = [
        *parse_mbs_xml(fixtures / "mbs_fragment.xml"),
        *parse_pbs_csv(fixtures / "pbs_fixture.csv"),
        *parse_cms_clfs_csv(fixtures / "cms_clfs_fixture.csv"),
        *parse_cms_pfs_csv(fixtures / "cms_pfs_fixture.csv"),
        *parse_cms_asp_csv(fixtures / "cms_asp_fixture.csv"),
    ]
    rows = schedule_item_vector_rows(schedule_records)
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = write_jsonl(rows, output_dir / "schedule_item_vectors.jsonl")
    csv_path = write_csv(rows, output_dir / "schedule_item_vectors.csv")
    arrow_path: str | None
    lance_path: str | None = None
    try:
        arrow_path = str(write_arrow_vector_seed(rows, output_dir / "schedule_item_vectors.arrow"))
    except VectorIndexDependencyError as exc:
        arrow_path = None
        console.print(f"Arrow vector seed skipped: {exc}")
    if build_lance:
        try:
            lance_path = str(build_lancedb_index(rows, database_dir=output_dir / "lancedb"))
        except VectorIndexDependencyError as exc:
            console.print(f"LanceDB vector seed skipped: {exc}")
    console.print_json(
        json.dumps(
            {
                "vector_rows": len(rows),
                "jsonl_path": str(jsonl_path),
                "csv_path": str(csv_path),
                "arrow_path": arrow_path,
                "lancedb_path": lance_path,
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
    files_ = load_source_files()
    ids_ = source_ids(sources_)
    missing = missing_analysis_sources(analyses_, ids_)
    missing_versions = missing_source_version_sources(versions_, ids_)
    duplicates = duplicate_source_ids(sources_)
    missing_status_sources = sorted({record.source_id for record in status_} - ids_)
    version_ids_ = {record.id for record in versions_}
    missing_file_sources = sorted({record.source_id for record in files_} - ids_)
    missing_file_versions = sorted({record.source_version_id for record in files_} - version_ids_)
    payload = {
        "source_count": len(sources_),
        "analysis_count": len(analyses_),
        "ontology_count": len(ontologies_),
        "source_version_count": len(versions_),
        "source_file_count": len(files_),
        "source_status_count": len(status_),
        "conductor_track_count": len(load_conductor_tracks()),
        "roadmap_function_count": len(load_roadmap_functions()),
        "dataset_candidate_count": len(load_dataset_candidates()),
        "mapping_resource_count": len(load_mapping_resources()),
        "research_question_count": len(load_research_questions()),
        "output_artifact_plan_count": len(load_output_artifact_plans()),
        "runtime_target_count": len(load_runtime_targets()),
        "access_tier_counts": access_tier_counts(sources_),
        "duplicate_source_ids": duplicates,
        "missing_analysis_sources": missing,
        "missing_source_version_sources": missing_versions,
        "missing_status_sources": missing_status_sources,
        "missing_file_sources": missing_file_sources,
        "missing_file_versions": missing_file_versions,
    }
    console.print_json(json.dumps(payload, indent=2))
    has_validation_errors = any((
        missing,
        missing_versions,
        missing_status_sources,
        missing_file_sources,
        missing_file_versions,
        duplicates,
    ))
    if has_validation_errors:
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
                "output_path": repo_relative(path),
            },
            indent=2,
        )
    )


def _load_osf_manifest_rows(path: Path) -> list[dict[str, object]]:
    """Load and validate the JSONL manifest used by the OSF planner."""
    if not path.exists():
        message = f"manifest does not exist: {path}"
        raise typer.BadParameter(message, param_hint="manifest_path")
    rows: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            message = f"manifest contains invalid JSON: line {exc.lineno}, column {exc.colno}"
            raise typer.BadParameter(message, param_hint="manifest_path") from exc
        if not isinstance(row, dict):
            message = f"manifest row on line {line_number} must be a JSON object"
            raise typer.BadParameter(message, param_hint="manifest_path")
        rows.append(cast("dict[str, object]", row))
    return rows


def _load_osf_remote_rows(path: Path | None) -> list[OsfRemoteRecord]:
    """Load and validate an exported JSON remote-state snapshot."""
    if path is None:
        return []
    if not path.exists():
        message = f"remote state does not exist: {path}"
        raise typer.BadParameter(message, param_hint="remote_state_path")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        message = f"remote state contains invalid JSON: line {exc.lineno}, column {exc.colno}"
        raise typer.BadParameter(message, param_hint="remote_state_path") from exc
    if not isinstance(payload, list):
        message = "remote state must be a JSON array"
        raise typer.BadParameter(message, param_hint="remote_state_path")

    remote_rows: list[OsfRemoteRecord] = []
    for row_number, raw_row in enumerate(cast("list[object]", payload), start=1):
        if not isinstance(raw_row, dict):
            message = f"remote state row {row_number} must be a JSON object"
            raise typer.BadParameter(message, param_hint="remote_state_path")
        row = cast("dict[str, object]", raw_row)
        osf_path = row.get("osf_path")
        byte_size = row.get("byte_size")
        if not isinstance(osf_path, str) or not isinstance(byte_size, int):
            message = f"remote state row {row_number} requires osf_path and integer byte_size"
            raise typer.BadParameter(message, param_hint="remote_state_path")
        sha256 = row.get("sha256")
        remote_rows.append(
            OsfRemoteRecord(
                osf_path=osf_path,
                sha256=sha256 if isinstance(sha256, str) else None,
                byte_size=byte_size,
                managed_by_manifest=bool(row.get("managed_by_manifest")),
            )
        )
    return remote_rows


@app.command("osf-reconcile")
def osf_reconcile(
    manifest_path: Annotated[
        Path,
        typer.Option(help="Generated OSF sync manifest in JSONL format."),
    ] = (project_root() / "data" / "derived" / "osf" / "sync_manifest.jsonl"),
    remote_state_path: Annotated[
        Path | None,
        typer.Option(help="JSON array containing the last exported remote OSF file state."),
    ] = None,
    output_path: Annotated[
        Path | None,
        typer.Option(help="Optional JSON reconciliation report output path."),
    ] = None,
    prune: Annotated[
        bool,
        typer.Option(
            help="Plan deletion only for remote rows explicitly managed by this manifest."
        ),
    ] = False,
) -> None:
    """Plan OSF mutations from local and exported remote state without network IO."""
    local_rows = _load_osf_manifest_rows(manifest_path)
    remote_rows = _load_osf_remote_rows(remote_state_path)
    actions = reconcile_osf_manifest(local_rows, remote_rows, prune=prune)
    report = {
        "manifest_path": repo_relative(manifest_path),
        "remote_state_path": repo_relative(remote_state_path) if remote_state_path else None,
        "prune": prune,
        "network_io": False,
        "mutation_performed": False,
        "actions": [asdict(action) for action in actions],
        "summary": {
            action: sum(1 for item in actions if item.action == action)
            for action in ("blocked", "create", "update", "skip", "delete")
        },
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    console.print_json(json.dumps(report, indent=2, sort_keys=True))


@app.command("osf-registration-check")
def osf_registration_check(
    freeze_path: Annotated[
        Path,
        typer.Option(help="Deterministic local OSF registration freeze JSON."),
    ] = (project_root() / "data" / "derived" / "osf" / "registration_freeze.json"),
    remote_state_path: Annotated[
        Path | None,
        typer.Option(help="Exported JSON OSF registration metadata snapshot."),
    ] = None,
    output_path: Annotated[
        Path | None,
        typer.Option(help="Optional JSON report destination."),
    ] = None,
) -> None:
    """Check an exported OSF registration snapshot for fingerprint drift."""
    if not freeze_path.exists():
        message = f"registration freeze does not exist: {freeze_path}"
        raise typer.BadParameter(message, param_hint="freeze_path")
    try:
        freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        message = f"registration freeze contains invalid JSON: {error}"
        raise typer.BadParameter(message, param_hint="freeze_path") from error
    if not isinstance(freeze, dict):
        message = "registration freeze must be a JSON object"
        raise typer.BadParameter(message, param_hint="freeze_path")
    freeze = cast("dict[str, object]", freeze)
    remote: dict[str, object] | None = None
    if remote_state_path is not None:
        if not remote_state_path.exists():
            message = f"remote registration snapshot does not exist: {remote_state_path}"
            raise typer.BadParameter(message, param_hint="remote_state_path")
        try:
            raw_remote = json.loads(remote_state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            message = f"remote registration snapshot contains invalid JSON: {error}"
            raise typer.BadParameter(message, param_hint="remote_state_path") from error
        if not isinstance(raw_remote, dict):
            message = "remote registration snapshot must be a JSON object"
            raise typer.BadParameter(message, param_hint="remote_state_path")
        remote = cast("dict[str, object]", raw_remote)
    report = check_registration_drift(freeze, remote)
    report["freeze_path"] = repo_relative(freeze_path)
    report["remote_state_path"] = repo_relative(remote_state_path) if remote_state_path else None
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    console.print_json(json.dumps(report, indent=2, sort_keys=True))


@app.command("repo-automation")
def repo_automation(
    output_dir: Annotated[
        Path,
        typer.Argument(help="Directory for repository automation policy artefacts."),
    ] = (project_root() / "data" / "derived" / "repo_automation"),
) -> None:
    """Write workflow-use, workflow-policy and automation-control tables."""
    root = project_root()
    output_dir.mkdir(parents=True, exist_ok=True)
    uses = [record.as_row() for record in scan_workflow_uses(root)]
    policy_records = workflow_policy_records(root)
    policies = [record.as_row() for record in policy_records]
    controls = [record.as_row() for record in automation_control_records(root)]
    sha_pin_plan = [
        {
            **row,
            "priority": "high" if row["pin_class"] in {"floating", "unknown"} else "medium",
            "recommended_action": (
                "Resolve the action tag to a 40-character commit SHA and preserve the "
                "human-readable version as a trailing comment."
            ),
        }
        for row in uses
        if row["pin_class"] not in {"sha", "local", "docker"}
    ]
    write_jsonl(uses, output_dir / "workflow_uses.jsonl")
    write_csv(uses, output_dir / "workflow_uses.csv")
    write_jsonl(policies, output_dir / "workflow_policy.jsonl")
    write_csv(policies, output_dir / "workflow_policy.csv")
    write_jsonl(controls, output_dir / "automation_controls.jsonl")
    write_csv(controls, output_dir / "automation_controls.csv")
    write_jsonl(sha_pin_plan, output_dir / "action_sha_pin_plan.jsonl")
    write_csv(sha_pin_plan, output_dir / "action_sha_pin_plan.csv")
    console.print_json(
        json.dumps(
            {
                "workflow_uses": len(uses),
                "workflow_policy_records": len(policies),
                "automation_controls": len(controls),
                "action_sha_pin_plan": len(sha_pin_plan),
                "summary": workflow_policy_summary(policy_records),
            },
            indent=2,
        )
    )


@app.command("local-quality-gates")
def local_quality_gates_command(
    profile: Annotated[
        str,
        typer.Option(help="Quality-gate profile: quick, ci, release or nightly."),
    ] = "ci",
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for local quality-gate run artefacts."),
    ] = (project_root() / "data" / "derived" / "local_quality_gates"),
    dry_run: Annotated[
        bool,
        typer.Option(help="Write planned gates without executing them."),
    ] = False,
) -> None:
    """Run or preview the local quality-gate profile used by CI/CD."""
    if profile not in {"quick", "ci", "release", "nightly"}:
        msg = "profile must be one of: quick, ci, release, nightly"
        raise typer.BadParameter(msg)
    records, summary = run_quality_gate_profile(
        cast("QualityGateProfile", profile),
        dry_run=dry_run,
    )
    paths = write_quality_gate_run(records, summary, output_dir=output_dir)
    console.print_json(
        json.dumps(
            {
                "summary": summary.as_row(),
                "paths": [repo_relative(path) for path in paths],
            },
            indent=2,
        )
    )
    if summary.blocking_failures and not dry_run:
        raise typer.Exit(code=1)


@app.command("sbom")
def sbom_command(
    output_dir: Annotated[
        Path,
        typer.Argument(help="Directory for generated CycloneDX SBOM files."),
    ] = (project_root() / "data" / "derived" / "sbom"),
) -> None:
    """Generate minimal CycloneDX SBOMs for Python and dashboard dependency locks."""
    output_dir.mkdir(parents=True, exist_ok=True)
    python_bom = build_python_sbom(project_root())
    dashboard_bom = build_dashboard_sbom(project_root())
    write_sbom(python_bom, output_dir / "cyclonedx-python.json")
    write_sbom(dashboard_bom, output_dir / "cyclonedx-dashboard.json")
    rows = [sbom_summary(python_bom), sbom_summary(dashboard_bom)]
    write_jsonl(rows, output_dir / "sbom_summary.jsonl")
    write_csv(rows, output_dir / "sbom_summary.csv")
    console.print_json(json.dumps({"sbom_count": len(rows), "rows": rows}, indent=2))


@app.command("architecture-report")
def architecture_report_command(
    output_dir: Annotated[
        Path,
        typer.Argument(help="Directory for generated architecture-boundary artefacts."),
    ] = (project_root() / "data" / "derived" / "architecture"),
) -> None:
    """Generate architecture-boundary import graph and layer-policy artefacts."""
    from reimburse_atlas.architecture import build_architecture_report, write_architecture_report

    report = build_architecture_report()
    paths = write_architecture_report(report, output_dir=output_dir)
    console.print_json(
        json.dumps(
            {"summary": report.summary.as_row(), "paths": [repo_relative(path) for path in paths]},
            indent=2,
        )
    )
    if not report.summary.architecture_ready:
        raise typer.Exit(code=1)


@app.command("release-readiness")
def release_readiness_command(
    output_dir: Annotated[
        Path,
        typer.Argument(help="Directory for generated release-readiness artefacts."),
    ] = (project_root() / "data" / "derived" / "release_readiness"),
    allow_blockers: Annotated[
        bool,
        typer.Option(help="Exit zero even when required release blockers remain."),
    ] = False,
) -> None:
    """Generate the consolidated public-release readiness matrix."""
    from reimburse_atlas.release_readiness import (
        build_release_readiness_report,
        write_release_readiness_report,
    )

    report = build_release_readiness_report()
    paths = write_release_readiness_report(report, output_dir=output_dir)
    console.print_json(
        json.dumps(
            {"summary": report.summary.as_row(), "paths": [repo_relative(path) for path in paths]},
            indent=2,
        )
    )
    if report.summary.required_blocker_count and not allow_blockers:
        raise typer.Exit(code=1)


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
    files_ = load_source_files()
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
        "source_file_count": len(files_),
        "source_status_count": len(status_),
        "conductor_track_count": len(load_conductor_tracks()),
        "roadmap_function_count": len(load_roadmap_functions()),
        "dataset_candidate_count": len(load_dataset_candidates()),
        "mapping_resource_count": len(load_mapping_resources()),
        "research_question_count": len(load_research_questions()),
        "output_artifact_plan_count": len(load_output_artifact_plans()),
        "runtime_target_count": len(load_runtime_targets()),
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
    from reimburse_atlas.analysis.mapping_evidence import MappingEvidenceRecord
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
        ConductorTrackRecord,
        DataAcquisitionAttemptRecord,
        DataDictionaryRecord,
        DataQualityCheckRecord,
        DatasetCandidateRecord,
        EvidenceReadinessRecord,
        FinalHandoffTaskRecord,
        GitHubProjectItemRecord,
        MappingResourceRecord,
        OntologyRecord,
        OutputArtifactPlanRecord,
        ProtocolStatusRecord,
        ResearchLinkageRecord,
        ResearchQuestionRecord,
        RoadmapFunctionRecord,
        RuntimeTargetRecord,
        SourceContentValidationRecord,
        SourceContractValidationRecord,
        SourceDriftRecord,
        SourceFileRecord,
        SourceRecord,
        SourceStatusRecord,
        SourceVersionRecord,
    )
    from reimburse_atlas.terminologies import OntologyConceptRecord, OntologyMappingTemplate

    output_dir.mkdir(parents=True, exist_ok=True)
    models = (
        SourceRecord,
        SourceStatusRecord,
        SourceFileRecord,
        AnalysisRecord,
        AnalysisRecipeRecord,
        OntologyRecord,
        SourceVersionRecord,
        ConductorTrackRecord,
        RoadmapFunctionRecord,
        DatasetCandidateRecord,
        MappingResourceRecord,
        ResearchQuestionRecord,
        OutputArtifactPlanRecord,
        RuntimeTargetRecord,
        ProtocolStatusRecord,
        DataAcquisitionAttemptRecord,
        SourceContentValidationRecord,
        SourceContractValidationRecord,
        DataQualityCheckRecord,
        FinalHandoffTaskRecord,
        GitHubProjectItemRecord,
        DataDictionaryRecord,
        ResearchLinkageRecord,
        EvidenceReadinessRecord,
        SourceDriftRecord,
        ProvenanceRecord,
        ScheduleItemRecord,
        SourceSnapshotRecord,
        CoverageDecisionRecord,
        CrosswalkCandidate,
        MappingEvidenceRecord,
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

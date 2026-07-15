"""Copy approved seed/derived CSV assets into the Astro dashboard public directory."""

from __future__ import annotations

import shutil
from pathlib import Path

from reimburse_atlas.registry import project_root

FILES = [
    Path("data/seed/graph_nodes.csv"),
    Path("data/seed/graph_edges.csv"),
    Path("data/seed/source_readiness.csv"),
    Path("data/seed/analysis_readiness.csv"),
    Path("data/seed/first_wave_ingestion_plan.csv"),
    Path("data/seed/source_acquisition_plan.csv"),
    Path("data/seed/source_files.csv"),
    Path("data/seed/ingestion_readiness.csv"),
    Path("data/derived/historical_sources/historical_mbs_archive_targets.csv"),
    Path("data/seed/source_snapshots.csv"),
    Path("data/seed/source_status.csv"),
    Path("data/seed/analysis_recipes.csv"),
    Path("data/seed/ontology_registry.csv"),
    Path("data/seed/ontology_concepts.csv"),
    Path("data/seed/ontology_mapping_templates.csv"),
    Path("data/derived/vertical_slice/schedule_items.csv"),
    Path("data/derived/vertical_slice/coverage_decisions.csv"),
    Path("data/derived/vertical_slice/crosswalk_candidates.csv"),
    Path("data/derived/vertical_slice/crosswalk_review_queue.csv"),
    Path("data/derived/vertical_slice/median_payment_by_source.csv"),
    Path("data/derived/vertical_slice/priced_share.csv"),
    Path("data/derived/vertical_slice/policy_signal_matrix.csv"),
    Path("data/derived/vertical_slice/mapping_evidence_matrix.csv"),
    Path("data/derived/vertical_slice/gold_standard_mappings.csv"),
    Path("data/derived/vertical_slice/negative_controls.csv"),
    Path("data/derived/vertical_slice/mapping_calibration_cases.csv"),
    Path("data/derived/vertical_slice/mapping_calibration_summary.csv"),
    Path("data/derived/manual_acquisition_pack/acquisition_steps.csv"),
    Path("data/derived/policy_demonstrators/policy_briefs.csv"),
    Path("data/derived/external_quality_gates.csv"),
    Path("data/derived/optional_toolchain_installs.csv"),
    Path("data/derived/repo_automation/workflow_uses.csv"),
    Path("data/derived/repo_automation/workflow_policy.csv"),
    Path("data/derived/repo_automation/automation_controls.csv"),
    Path("data/derived/repo_automation/action_sha_pin_plan.csv"),
    Path("data/derived/repo_automation/action_pin_resolution.csv"),
    Path("data/derived/sbom/sbom_summary.csv"),
    Path("data/derived/local_quality_gates/local_quality_gates.csv"),
    Path("data/derived/local_quality_gates/local_quality_gate_specs.csv"),
    Path("data/derived/architecture/import_edges.csv"),
    Path("data/derived/architecture/layer_policy.csv"),
    Path("data/derived/architecture/import_cycles.csv"),
    Path("data/derived/release_readiness/release_gates.csv"),
    Path("data/derived/licence_review/licence_review_queue.csv"),
    Path("data/seed/conductor_tracks.csv"),
    Path("data/seed/roadmap_functions.csv"),
    Path("data/seed/dataset_candidates.csv"),
    Path("data/seed/mapping_resources.csv"),
    Path("data/seed/research_questions.csv"),
    Path("data/seed/output_artifact_plans.csv"),
    Path("data/seed/runtime_targets.csv"),
    Path("data/derived/source_downloads/download_plans.csv"),
    Path("data/derived/source_downloads/download_attempts.csv"),
    Path("data/derived/source_downloads/pbs_api_acquisition.csv"),
    Path("data/derived/source_validation/source_content_validation.csv"),
    Path("data/derived/source_contracts/source_contract_validation.csv"),
    Path("data/derived/github_project/github_project_items.csv"),
    Path("data/derived/final_handoff/final_handoff_tasks.csv"),
    Path("data/derived/protocols/protocol_status.csv"),
    Path("data/derived/roadmap_linkages/research_dataset_linkages.csv"),
    Path("data/derived/data_quality/data_quality_checks.csv"),
    Path("data/derived/evidence_readiness/evidence_readiness.csv"),
    Path("data/derived/source_drift/source_drift_report.csv"),
    Path("data/derived/data_dictionary/data_dictionary.csv"),
    Path("data/derived/source_health/acquisition_status.csv"),
]

PUBLIC_PATH_REPLACEMENTS = {
    "data/raw_live": "[ignored-local-raw-cache]",
}


def sanitise_public_text(text: str) -> str:
    """Remove local-only cache paths before copying derived assets publicly."""
    for source, replacement in PUBLIC_PATH_REPLACEMENTS.items():
        text = text.replace(source, replacement)
    return text


def main() -> None:
    """Synchronise dashboard-safe generated CSV files."""
    root = project_root()
    output_dir = root / "apps" / "dashboard" / "public" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for relative_path in FILES:
        source = root / relative_path
        if not source.exists():
            continue
        target = output_dir / source.name
        if source.suffix.lower() == ".csv":
            target.write_text(
                sanitise_public_text(source.read_text(encoding="utf-8")),
                encoding="utf-8",
            )
        else:
            shutil.copy2(source, target)
        copied += 1
    print(f"Copied {copied} dashboard seed files to {output_dir}")


if __name__ == "__main__":
    main()

"""Publication-manifest helpers for derived and seed data exports."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from reimburse_atlas.registry import project_root


@dataclass(frozen=True)
class PublicationArtifact:
    """One file that may be included in a public derived-data release."""

    table_name: str
    relative_path: str
    file_format: str
    row_count: int
    byte_size: int
    checksum_sha256: str
    publication_scope: str
    licence_gate: str
    contains_raw_source_payload: bool
    notes: str


@dataclass(frozen=True)
class PublicationManifest:
    """Manifest describing a candidate public/Hugging Face dataset release."""

    project: str
    manifest_version: str
    artifact_count: int
    artifacts: tuple[PublicationArtifact, ...]
    warnings: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation."""
        return asdict(self)


DEFAULT_PUBLICATION_PATHS = (
    Path("data/seed/source_registry.jsonl"),
    Path("data/seed/source_registry.csv"),
    Path("data/seed/source_versions.jsonl"),
    Path("data/seed/source_versions.csv"),
    Path("data/seed/source_files.jsonl"),
    Path("data/seed/source_files.csv"),
    Path("data/seed/source_status.jsonl"),
    Path("data/seed/source_status.csv"),
    Path("data/seed/source_snapshots.jsonl"),
    Path("data/seed/source_snapshots.csv"),
    Path("data/seed/analysis_catalogue.jsonl"),
    Path("data/seed/analysis_catalogue.csv"),
    Path("data/seed/analysis_recipes.jsonl"),
    Path("data/seed/analysis_recipes.csv"),
    Path("data/seed/ontology_registry.jsonl"),
    Path("data/seed/ontology_registry.csv"),
    Path("data/seed/ontology_concepts.jsonl"),
    Path("data/seed/ontology_concepts.csv"),
    Path("data/seed/graph_nodes.csv"),
    Path("data/seed/graph_edges.csv"),
    Path("data/seed/conductor_tracks.jsonl"),
    Path("data/seed/conductor_tracks.csv"),
    Path("data/seed/roadmap_functions.jsonl"),
    Path("data/seed/roadmap_functions.csv"),
    Path("data/seed/dataset_candidates.jsonl"),
    Path("data/seed/dataset_candidates.csv"),
    Path("data/seed/mapping_resources.jsonl"),
    Path("data/seed/mapping_resources.csv"),
    Path("data/seed/research_questions.jsonl"),
    Path("data/seed/research_questions.csv"),
    Path("data/seed/output_artifact_plans.jsonl"),
    Path("data/seed/output_artifact_plans.csv"),
    Path("data/seed/runtime_targets.jsonl"),
    Path("data/seed/runtime_targets.csv"),
    Path("data/seed/source_readiness.csv"),
    Path("data/seed/analysis_readiness.csv"),
    Path("data/seed/source_acquisition_plan.csv"),
    Path("data/seed/ingestion_readiness.csv"),
    Path("data/seed/historical_mbs_archive_targets.jsonl"),
    Path("data/derived/historical_sources/historical_mbs_archive_targets.jsonl"),
    Path("data/derived/historical_sources/historical_mbs_archive_targets.csv"),
    Path("data/derived/historical_sources/historical_mbs_review_queue.jsonl"),
    Path("data/derived/historical_sources/historical_mbs_review_queue.csv"),
    Path("data/derived/historical_sources/summary.json"),
    Path("data/derived/historical_sources/historical_source_downloads.jsonl"),
    Path("data/derived/historical_sources/historical_source_downloads.csv"),
    Path("data/derived/historical_sources/historical_source_downloads_summary.json"),
    Path("data/derived/historical_sources/historical_source_catalog.jsonl"),
    Path("data/derived/historical_sources/family_archive_v2/historical_source_downloads.jsonl"),
    Path("data/derived/historical_sources/family_archive_v2/historical_source_downloads.csv"),
    Path(
        "data/derived/historical_sources/family_archive_v2/historical_source_downloads_summary.json"
    ),
    Path("data/derived/processes/historical_source_transformation.bpmn"),
    Path("data/derived/vertical_slice/schedule_items.jsonl"),
    Path("data/derived/vertical_slice/schedule_items.csv"),
    Path("data/derived/vertical_slice/coverage_decisions.jsonl"),
    Path("data/derived/vertical_slice/coverage_decisions.csv"),
    Path("data/derived/vertical_slice/crosswalk_candidates.jsonl"),
    Path("data/derived/vertical_slice/crosswalk_candidates.csv"),
    Path("data/derived/vertical_slice/crosswalk_review_queue.jsonl"),
    Path("data/derived/vertical_slice/crosswalk_review_queue.csv"),
    Path("data/derived/vertical_slice/policy_signal_matrix.jsonl"),
    Path("data/derived/vertical_slice/policy_signal_matrix.csv"),
    Path("data/derived/vertical_slice/mapping_evidence_matrix.jsonl"),
    Path("data/derived/vertical_slice/mapping_evidence_matrix.csv"),
    Path("data/derived/vertical_slice/gold_standard_mappings.jsonl"),
    Path("data/derived/vertical_slice/gold_standard_mappings.csv"),
    Path("data/derived/vertical_slice/negative_controls.jsonl"),
    Path("data/derived/vertical_slice/negative_controls.csv"),
    Path("data/derived/vertical_slice/mapping_calibration_cases.jsonl"),
    Path("data/derived/vertical_slice/mapping_calibration_cases.csv"),
    Path("data/derived/vertical_slice/mapping_calibration_summary.jsonl"),
    Path("data/derived/vertical_slice/mapping_calibration_summary.csv"),
    Path("data/derived/vertical_slice/mapping_review_status.jsonl"),
    Path("data/derived/vertical_slice/mapping_review_status.csv"),
    Path("data/derived/manual_acquisition_pack/acquisition_steps.jsonl"),
    Path("data/derived/manual_acquisition_pack/acquisition_steps.csv"),
    Path("data/derived/policy_demonstrators/policy_briefs.jsonl"),
    Path("data/derived/policy_demonstrators/policy_briefs.csv"),
    Path("data/derived/policy_demonstrators/policy_briefs.md"),
    Path("data/derived/policy_demonstrators/summary.json"),
    Path("data/derived/external_quality_gates.json"),
    Path("data/derived/external_quality_gates.csv"),
    Path("data/derived/optional_toolchain_installs.json"),
    Path("data/derived/optional_toolchain_installs.csv"),
    Path("data/derived/toolchain/typescript_compatibility.json"),
    Path("data/derived/toolchain/typescript_compatibility.md"),
    Path("data/derived/repo_automation/workflow_uses.jsonl"),
    Path("data/derived/repo_automation/workflow_uses.csv"),
    Path("data/derived/repo_automation/workflow_policy.jsonl"),
    Path("data/derived/repo_automation/workflow_policy.csv"),
    Path("data/derived/repo_automation/automation_controls.jsonl"),
    Path("data/derived/repo_automation/automation_controls.csv"),
    Path("data/derived/repo_automation/action_sha_pin_plan.jsonl"),
    Path("data/derived/repo_automation/action_sha_pin_plan.csv"),
    Path("data/derived/repo_automation/action_pin_resolution.jsonl"),
    Path("data/derived/repo_automation/action_pin_resolution.csv"),
    Path("data/derived/sbom/sbom_summary.jsonl"),
    Path("data/derived/sbom/sbom_summary.csv"),
    Path("data/derived/sbom/cyclonedx-python.json"),
    Path("data/derived/sbom/cyclonedx-dashboard.json"),
    Path("data/derived/local_quality_gates/local_quality_gates.jsonl"),
    Path("data/derived/local_quality_gates/local_quality_gates.csv"),
    Path("data/derived/local_quality_gates/local_quality_gate_specs.jsonl"),
    Path("data/derived/local_quality_gates/local_quality_gate_specs.csv"),
    Path("data/derived/architecture/import_edges.jsonl"),
    Path("data/derived/architecture/import_edges.csv"),
    Path("data/derived/architecture/layer_policy.jsonl"),
    Path("data/derived/architecture/layer_policy.csv"),
    Path("data/derived/architecture/import_cycles.jsonl"),
    Path("data/derived/architecture/import_cycles.csv"),
    Path("data/derived/release_readiness/release_gates.jsonl"),
    Path("data/derived/release_readiness/release_gates.csv"),
    Path("data/derived/v13_validation_run.json"),
    Path("data/derived/source_downloads/download_plans.jsonl"),
    Path("data/derived/source_downloads/download_plans.csv"),
    Path("data/derived/source_downloads/download_attempts.jsonl"),
    Path("data/derived/source_downloads/download_attempts.csv"),
    Path("data/derived/source_downloads/pbs_api_acquisition.jsonl"),
    Path("data/derived/source_downloads/pbs_api_acquisition.csv"),
    Path("data/derived/source_downloads/pbs_api_acquisition_summary.json"),
    Path("data/derived/source_validation/source_content_validation.jsonl"),
    Path("data/derived/source_validation/source_content_validation.csv"),
    Path("data/derived/source_contracts/source_contract_validation.jsonl"),
    Path("data/derived/source_contracts/source_contract_validation.csv"),
    Path("data/derived/github_project/github_project_items.jsonl"),
    Path("data/derived/github_project/github_project_items.csv"),
    Path("data/derived/final_handoff/final_handoff_tasks.jsonl"),
    Path("data/derived/final_handoff/final_handoff_tasks.csv"),
    Path("data/derived/osf/component_plan.jsonl"),
    Path("data/derived/osf/component_plan.csv"),
    Path("data/derived/osf/osf_publication_manifest.json"),
    Path("data/derived/osf/preprint_checklist.md"),
    Path("data/derived/osf/sync_manifest.jsonl"),
    Path("data/derived/protocols/protocol_status.jsonl"),
    Path("data/derived/protocols/protocol_status.csv"),
    Path("data/derived/protocols/summary.json"),
    Path("data/derived/roadmap_linkages/research_dataset_linkages.jsonl"),
    Path("data/derived/roadmap_linkages/research_dataset_linkages.csv"),
    Path("data/derived/data_quality/data_quality_checks.jsonl"),
    Path("data/derived/data_quality/data_quality_checks.csv"),
    Path("data/derived/data_quality/summary.json"),
    Path("data/derived/evidence_readiness/evidence_readiness.jsonl"),
    Path("data/derived/evidence_readiness/evidence_readiness.csv"),
    Path("data/derived/evidence_readiness/summary.json"),
    Path("data/derived/source_drift/source_drift_report.jsonl"),
    Path("data/derived/source_drift/source_drift_report.csv"),
    Path("data/derived/source_drift/summary.json"),
    Path("data/derived/data_dictionary/data_dictionary.jsonl"),
    Path("data/derived/data_dictionary/data_dictionary.csv"),
    Path("data/derived/data_dictionary/summary.json"),
    Path("infra/huggingface/DATASET_CARD.md"),
    Path("infra/huggingface/CROISSANT.json"),
    Path("infra/huggingface/README.md"),
    Path("infra/huggingface/SPACE_README.md"),
    Path("data/derived/research_package/datapackage.json"),
    Path("data/derived/research_package/ro-crate-metadata.json"),
    Path("data/derived/research_package/dcat.jsonld"),
    Path("data/derived/mojo/mojo_parity_report.json"),
    Path("data/derived/mojo/fuzzy_prefilter_benchmark.json"),
    Path("data/derived/v14_validation_run.json"),
    Path("data/derived/v15_validation_run.json"),
    Path("data/derived/v16_validation_run.json"),
    Path("data/derived/v17_validation_run.json"),
    Path("data/derived/v18_validation_run.json"),
)

PROJECT_OWNED_METADATA_PREFIXES = (
    Path("data/derived/data_dictionary"),
    Path("data/derived/final_handoff"),
    Path("data/derived/local_quality_gates"),
    Path("data/derived/release_readiness"),
    Path("data/derived/research_package"),
    Path("data/derived/source_drift"),
)


def file_sha256(path: Path) -> str:
    """Return a SHA-256 checksum for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_rows(path: Path) -> int:
    """Count data rows in a JSONL or CSV artefact."""
    if path.suffix == ".jsonl":
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    if path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            return max(sum(1 for _ in csv.reader(handle)) - 1, 0)
    return 0


def reviewed_source_bundle_paths(root: Path) -> tuple[Path, ...]:
    """Return nested reviewed-bundle files without including raw payloads."""
    bundle_root = root / "data" / "derived" / "reviewed_source_bundles"
    if not bundle_root.exists():
        return ()
    return tuple(
        sorted(
            path.relative_to(root)
            for path in bundle_root.glob("*/*")
            if path.is_file() and path.name != "publication_manifest.json"
        )
    )


def _scope_for(path: Path) -> tuple[str, str, bool, str]:
    parts = set(path.parts)
    if "raw" in parts or "raw_live" in parts or "local" in parts or "cache" in parts:
        return (
            "excluded",
            "raw_or_local_cache",
            True,
            "Raw/cache path detected; do not publish.",
        )
    if any(path.is_relative_to(prefix) for prefix in PROJECT_OWNED_METADATA_PREFIXES):
        return (
            "project_owned_metadata",
            "apache_2_0_project_output",
            False,
            "Project-authored operational metadata; covered by the repository Apache-2.0 licence.",
        )
    if "derived" in parts:
        return (
            "public_derived_candidate",
            "public_reuse_review",
            False,
            "Derived artefact; review source-specific licence notes before external publication.",
        )
    return (
        "public_metadata_candidate",
        "public_reuse_review",
        False,
        "Metadata/seed artefact; review source URLs and licence notes before external publication.",
    )


def build_publication_manifest(
    paths: tuple[Path, ...] = DEFAULT_PUBLICATION_PATHS,
    root: Path | None = None,
) -> PublicationManifest:
    """Build a manifest for the curated release candidate files that currently exist."""
    repo_root = root or project_root()
    artifacts: list[PublicationArtifact] = []
    warnings: list[str] = []
    candidate_paths = tuple(dict.fromkeys((*paths, *reviewed_source_bundle_paths(repo_root))))
    for relative_path in candidate_paths:
        path = repo_root / relative_path
        if not path.exists():
            continue
        scope, gate, contains_raw, notes = _scope_for(relative_path)
        if contains_raw:
            warnings.append(f"Excluded raw/cache path from release manifest: {relative_path}")
            continue
        artifacts.append(
            PublicationArtifact(
                table_name=relative_path.stem,
                relative_path=str(relative_path),
                file_format=relative_path.suffix.lstrip(".") or "unknown",
                row_count=count_rows(path),
                byte_size=path.stat().st_size,
                checksum_sha256=file_sha256(path),
                publication_scope=scope,
                licence_gate=gate,
                contains_raw_source_payload=contains_raw,
                notes=notes,
            )
        )
    return PublicationManifest(
        project="reimbursement-atlas-conductor",
        manifest_version="v1",
        artifact_count=len(artifacts),
        artifacts=tuple(artifacts),
        warnings=tuple(warnings),
    )


def write_publication_manifest(manifest: PublicationManifest, output_path: Path) -> Path:
    """Write a publication manifest as deterministic JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest.as_dict(), indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    return output_path

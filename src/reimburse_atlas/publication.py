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
    Path("data/seed/source_readiness.csv"),
    Path("data/seed/analysis_readiness.csv"),
    Path("data/seed/source_acquisition_plan.csv"),
    Path("data/seed/ingestion_readiness.csv"),
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
    Path("data/derived/manual_acquisition_pack/acquisition_steps.jsonl"),
    Path("data/derived/manual_acquisition_pack/acquisition_steps.csv"),
    Path("data/derived/external_quality_gates.json"),
    Path("data/derived/external_quality_gates.csv"),
    Path("data/derived/optional_toolchain_installs.json"),
    Path("data/derived/optional_toolchain_installs.csv"),
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


def _scope_for(path: Path) -> tuple[str, str, bool, str]:
    parts = set(path.parts)
    if "raw" in parts or "raw_live" in parts or "local" in parts or "cache" in parts:
        return (
            "excluded",
            "raw_or_local_cache",
            True,
            "Raw/cache path detected; do not publish.",
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
    for relative_path in paths:
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

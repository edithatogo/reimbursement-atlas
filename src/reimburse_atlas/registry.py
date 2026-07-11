"""Registry loaders and validators."""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import TypeVar, cast

from pydantic import BaseModel

from reimburse_atlas.contracts import SourceSnapshotRecord
from reimburse_atlas.models import (
    AnalysisRecipeRecord,
    AnalysisRecord,
    ConductorTrackRecord,
    DataAcquisitionAttemptRecord,
    DatasetCandidateRecord,
    MappingResourceRecord,
    OntologyRecord,
    OutputArtifactPlanRecord,
    ResearchQuestionRecord,
    RoadmapFunctionRecord,
    RuntimeTargetRecord,
    SourceFileRecord,
    SourceRecord,
    SourceStatusRecord,
    SourceVersionRecord,
)
from reimburse_atlas.terminologies import OntologyConceptRecord, OntologyMappingTemplate

T = TypeVar("T", bound=BaseModel)


def project_root() -> Path:
    """Return the repository root for an editable checkout."""
    override = os.environ.get("REIMBURSE_ATLAS_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def repo_relative(path: Path, root: Path | None = None) -> str:
    """Return a repo-relative path string when possible."""
    repo = root or project_root()
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def stable_generated_at() -> str:
    """Return a reproducible timestamp for generated artefacts.

    The timestamp defaults to the SOURCE_DATE_EPOCH convention so regenerated
    outputs stay stable across local and CI environments. When the environment
    does not provide a source date, the epoch is used as a deterministic
    fallback rather than the current wall clock.
    """
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "0"))
    return datetime.fromtimestamp(epoch, tz=UTC).isoformat()


def read_jsonl(path: Path) -> list[dict[str, object]]:
    """Read newline-delimited JSON records."""
    records: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        loaded = json.loads(line)
        if not isinstance(loaded, dict):
            msg = f"{path}:{line_number} is not a JSON object"
            raise TypeError(msg)
        records.append(cast("dict[str, object]", loaded))
    return records


def parse_records(model: type[T], rows: Iterable[dict[str, object]]) -> list[T]:
    """Parse raw rows with a pydantic model."""
    return [model.model_validate(row) for row in rows]


def load_source_registry(path: Path | None = None) -> list[SourceRecord]:
    """Load the source registry."""
    registry_path = path or project_root() / "data" / "seed" / "source_registry.jsonl"
    return parse_records(SourceRecord, read_jsonl(registry_path))


def load_source_versions(path: Path | None = None) -> list[SourceVersionRecord]:
    """Load registered source versions and parser targets."""
    versions_path = path or project_root() / "data" / "seed" / "source_versions.jsonl"
    return parse_records(SourceVersionRecord, read_jsonl(versions_path))


def load_analysis_catalogue(path: Path | None = None) -> list[AnalysisRecord]:
    """Load the analysis catalogue."""
    catalogue_path = path or project_root() / "data" / "seed" / "analysis_catalogue.jsonl"
    return parse_records(AnalysisRecord, read_jsonl(catalogue_path))


def load_ontology_registry(path: Path | None = None) -> list[OntologyRecord]:
    """Load the ontology registry."""
    registry_path = path or project_root() / "data" / "seed" / "ontology_registry.jsonl"
    return parse_records(OntologyRecord, read_jsonl(registry_path))


def source_ids(records: Iterable[SourceRecord]) -> set[str]:
    """Return source ids from source records."""
    return {record.id for record in records}


def load_source_snapshots(path: Path | None = None) -> list[SourceSnapshotRecord]:
    """Load source snapshot provenance records."""
    snapshots_path = path or project_root() / "data" / "seed" / "source_snapshots.jsonl"
    return parse_records(SourceSnapshotRecord, read_jsonl(snapshots_path))


def load_source_status(path: Path | None = None) -> list[SourceStatusRecord]:
    """Load current source-status observations."""
    status_path = path or project_root() / "data" / "seed" / "source_status.jsonl"
    return parse_records(SourceStatusRecord, read_jsonl(status_path))


def load_source_files(path: Path | None = None) -> list[SourceFileRecord]:
    """Load exact source-file, landing-page and endpoint acquisition records."""
    files_path = path or project_root() / "data" / "seed" / "source_files.jsonl"
    if not files_path.exists():
        return []
    return parse_records(SourceFileRecord, read_jsonl(files_path))


def load_analysis_recipes(path: Path | None = None) -> list[AnalysisRecipeRecord]:
    """Load machine-readable analysis recipes when present."""
    recipes_path = path or project_root() / "data" / "seed" / "analysis_recipes.jsonl"
    if not recipes_path.exists():
        return []
    return parse_records(AnalysisRecipeRecord, read_jsonl(recipes_path))


def load_ontology_concepts(path: Path | None = None) -> list[OntologyConceptRecord]:
    """Load small local ontology concept seed rows when present."""
    concepts_path = path or project_root() / "data" / "seed" / "ontology_concepts.jsonl"
    if not concepts_path.exists():
        return []
    return parse_records(OntologyConceptRecord, read_jsonl(concepts_path))


def load_ontology_mapping_templates(path: Path | None = None) -> list[OntologyMappingTemplate]:
    """Load ontology mapping-template seed rows when present."""
    templates_path = path or project_root() / "data" / "seed" / "ontology_mapping_templates.jsonl"
    if not templates_path.exists():
        return []
    return parse_records(OntologyMappingTemplate, read_jsonl(templates_path))


def _load_optional_seed(model: type[T], table_name: str, path: Path | None = None) -> list[T]:
    """Load an optional seed table with a pydantic model."""
    table_path = path or project_root() / "data" / "seed" / f"{table_name}.jsonl"
    if not table_path.exists():
        return []
    return parse_records(model, read_jsonl(table_path))


def load_conductor_tracks(path: Path | None = None) -> list[ConductorTrackRecord]:
    """Load machine-readable Conductor implementation tracks."""
    return _load_optional_seed(ConductorTrackRecord, "conductor_tracks", path)


def load_roadmap_functions(path: Path | None = None) -> list[RoadmapFunctionRecord]:
    """Load planned roadmap functions and interfaces."""
    return _load_optional_seed(RoadmapFunctionRecord, "roadmap_functions", path)


def load_dataset_candidates(path: Path | None = None) -> list[DatasetCandidateRecord]:
    """Load proposed additional datasets and country/source candidates."""
    return _load_optional_seed(DatasetCandidateRecord, "dataset_candidates", path)


def load_mapping_resources(path: Path | None = None) -> list[MappingResourceRecord]:
    """Load proposed ontology and mapping resources."""
    return _load_optional_seed(MappingResourceRecord, "mapping_resources", path)


def load_research_questions(path: Path | None = None) -> list[ResearchQuestionRecord]:
    """Load pre-specified research questions."""
    return _load_optional_seed(ResearchQuestionRecord, "research_questions", path)


def load_output_artifact_plans(path: Path | None = None) -> list[OutputArtifactPlanRecord]:
    """Load planned publication and deployment outputs."""
    return _load_optional_seed(OutputArtifactPlanRecord, "output_artifact_plans", path)


def load_runtime_targets(path: Path | None = None) -> list[RuntimeTargetRecord]:
    """Load language/toolchain runtime targets."""
    return _load_optional_seed(RuntimeTargetRecord, "runtime_targets", path)


def load_data_acquisition_attempts(path: Path | None = None) -> list[DataAcquisitionAttemptRecord]:
    """Load local acquisition-attempt records when generated."""
    table_path = (
        path or project_root() / "data" / "derived" / "source_downloads" / "download_attempts.jsonl"
    )
    if not table_path.exists():
        return []
    return parse_records(DataAcquisitionAttemptRecord, read_jsonl(table_path))

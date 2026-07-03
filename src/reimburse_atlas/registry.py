"""Registry loaders and validators."""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from pathlib import Path
from typing import TypeVar, cast

from pydantic import BaseModel

from reimburse_atlas.contracts import SourceSnapshotRecord
from reimburse_atlas.models import (
    AnalysisRecipeRecord,
    AnalysisRecord,
    OntologyRecord,
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

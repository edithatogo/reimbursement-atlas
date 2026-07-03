"""Local-only terminology concept seed helpers.

The project deliberately keeps licence-restricted ontology dumps out of git.
This module supports small synthetic/permissive seed concepts and future local
adapter contracts for LOINC, ATC, HPO, RxNorm/RxNav and related mappings.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Literal

from pydantic import Field

from reimburse_atlas.models import FrozenModel, NonEmptyStr, SourceId
from reimburse_atlas.parsers.normalise import clean_text


class OntologyConceptRecord(FrozenModel):
    """Small concept record for local ontology graph and mapping prototypes."""

    terminology_id: SourceId
    code: NonEmptyStr
    label: NonEmptyStr
    domain: NonEmptyStr
    concept_class: NonEmptyStr
    licence_scope: Literal["synthetic", "permissive", "local_only", "restricted"]
    synonyms: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    mapping_targets: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    notes: NonEmptyStr


class OntologyMappingTemplate(FrozenModel):
    """Template for a reviewable mapping assertion between terminology families."""

    left_terminology_id: SourceId
    left_code: NonEmptyStr
    right_terminology_id: SourceId
    right_code: NonEmptyStr
    relationship: Literal["exact", "narrower", "broader", "related", "candidate"]
    review_status: Literal["template", "machine_generated", "reviewed", "rejected"] = "template"
    evidence_method: NonEmptyStr
    notes: NonEmptyStr


def _split_pipe(value: object | None) -> tuple[str, ...]:
    text = clean_text(value)
    if text is None:
        return ()
    return tuple(part.strip() for part in text.split("|") if part.strip())


def parse_ontology_concepts_csv(path: Path) -> list[OntologyConceptRecord]:
    """Parse a small ontology-concept seed CSV file."""
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        return [
            OntologyConceptRecord(
                terminology_id=str(row["terminology_id"]).strip(),
                code=str(row["code"]).strip(),
                label=str(row["label"]).strip(),
                domain=str(row["domain"]).strip(),
                concept_class=str(row["concept_class"]).strip(),
                licence_scope=str(row["licence_scope"]).strip(),  # type: ignore[arg-type]
                synonyms=_split_pipe(row.get("synonyms")),
                mapping_targets=_split_pipe(row.get("mapping_targets")),
                notes=str(row["notes"]).strip(),
            )
            for row in rows
        ]


def build_mapping_templates(concepts: list[OntologyConceptRecord]) -> list[OntologyMappingTemplate]:
    """Build deterministic mapping-template rows from concept target hints."""
    by_key = {(concept.terminology_id, concept.code): concept for concept in concepts}
    templates: list[OntologyMappingTemplate] = []
    for concept in concepts:
        for target in concept.mapping_targets:
            if ":" not in target:
                continue
            right_terminology_id, right_code = target.split(":", 1)
            if (right_terminology_id, right_code) not in by_key:
                continue
            templates.append(
                OntologyMappingTemplate(
                    left_terminology_id=concept.terminology_id,
                    left_code=concept.code,
                    right_terminology_id=right_terminology_id,
                    right_code=right_code,
                    relationship="candidate",
                    evidence_method="seed_mapping_target_hint",
                    notes="Synthetic mapping template for review workflow testing only.",
                )
            )
    return sorted(
        templates,
        key=lambda row: (
            row.left_terminology_id,
            row.left_code,
            row.right_terminology_id,
            row.right_code,
        ),
    )

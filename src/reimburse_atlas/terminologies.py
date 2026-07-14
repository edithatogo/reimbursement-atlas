"""Local-only terminology concept seed helpers.

The project deliberately keeps licence-restricted ontology dumps out of git.
This module supports small synthetic/permissive seed concepts and future local
adapter contracts for LOINC, ATC, HPO, RxNorm/RxNav and related mappings.
"""

from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path
from typing import Literal, cast

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


class RxNavAdapterConfig(FrozenModel):
    """Local endpoint contract for an RxNav or RxNav-in-a-Box service."""

    base_url: str = Field(default="http://localhost:8000/", pattern=r"^https?://[^\s]+$")
    timeout_seconds: float = Field(default=10.0, gt=0, le=120)
    licence_scope: Literal["local_only", "permissive", "review_required"] = "local_only"


class RxNavConceptQuery(FrozenModel):
    """Read-only RxNav lookup request without embedding a terminology payload."""

    term: NonEmptyStr
    max_results: int = Field(default=20, ge=1, le=100)


class RxNavConceptMatch(FrozenModel):
    """Minimal derived match returned by a local RxNav-compatible adapter."""

    rxcui: NonEmptyStr
    label: NonEmptyStr


def build_rxnav_approximate_match_url(config: RxNavAdapterConfig, query: RxNavConceptQuery) -> str:
    """Build a deterministic RxNav approximate-match URL without making a request."""
    from urllib.parse import urlencode

    base = str(config.base_url).rstrip("/")
    params = urlencode({"term": query.term, "maxEntries": query.max_results})
    return f"{base}/REST/approximateTerm.json?{params}"


def parse_rxnav_matches(payload: Mapping[str, object]) -> list[RxNavConceptMatch]:
    """Parse only stable RxNav identifiers and labels from a JSON-like payload."""
    candidates_raw = payload.get("approximateGroup")
    if not isinstance(candidates_raw, Mapping):
        return []
    candidates = cast("Mapping[str, object]", candidates_raw)
    raw_matches = candidates.get("candidate")
    if not isinstance(raw_matches, list):
        return []
    raw_matches = cast("list[object]", raw_matches)
    matches: list[RxNavConceptMatch] = []
    for raw_match in raw_matches:
        if not isinstance(raw_match, Mapping):
            continue
        raw_match = cast("Mapping[str, object]", raw_match)
        rxcui = raw_match.get("rxcui")
        label = raw_match.get("name")
        if isinstance(rxcui, str) and isinstance(label, str) and rxcui.strip() and label.strip():
            matches.append(RxNavConceptMatch(rxcui=rxcui.strip(), label=label.strip()))
    return matches


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

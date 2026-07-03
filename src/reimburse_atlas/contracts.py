"""Typed contracts for schedule items, mappings and provenance.

These contracts are intentionally conservative. They describe what the atlas
will standardise after source-specific parsers have extracted raw records, not
what every source natively provides.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import Annotated, Literal, cast

from pydantic import Field, HttpUrl, field_validator

from reimburse_atlas.models import FrozenModel, NonEmptyStr, SourceId

Confidence = Annotated[float, Field(ge=0.0, le=1.0)]
CrosswalkRelationship = Literal["exact", "narrower", "broader", "related", "unmapped"]
OptionalNonEmptyStr = Annotated[str | None, Field(min_length=1)]


class ProvenanceRecord(FrozenModel):
    """Minimal provenance metadata for a derived record."""

    source_id: SourceId
    source_url: HttpUrl | None = None
    retrieved_at: OptionalNonEmptyStr = None
    effective_date: date | None = None
    source_version: OptionalNonEmptyStr = None
    licence_class: Literal[
        "permissive",
        "public_reuse_unclear",
        "restricted",
        "unknown",
    ] = "unknown"
    transformation_notes: OptionalNonEmptyStr = None


class SourceSnapshotRecord(FrozenModel):
    """Metadata for a local source snapshot or derived-only acquisition event."""

    id: SourceId
    source_id: SourceId
    source_version_id: SourceId
    source_url: HttpUrl
    local_path: OptionalNonEmptyStr = None
    retrieved_at: NonEmptyStr
    content_type: OptionalNonEmptyStr = None
    byte_size: int | None = Field(default=None, ge=0)
    checksum_sha256: OptionalNonEmptyStr = None
    licence_gate: Literal[
        "permissive",
        "public_reuse_review",
        "restricted_local_only",
    ]
    cache_scope: Literal[
        "public_raw_cache",
        "public_derived_only",
        "local_raw_only",
        "metadata_only",
    ]
    notes: OptionalNonEmptyStr = None


class ScheduleItemRecord(FrozenModel):
    """Normalised schedule item after source-specific parsing."""

    source_id: SourceId
    jurisdiction: NonEmptyStr
    domain: NonEmptyStr
    code_system: NonEmptyStr
    item_code: NonEmptyStr
    item_label: NonEmptyStr
    item_description: OptionalNonEmptyStr = None
    payment_amount: float | None = Field(default=None, ge=0.0)
    currency: OptionalNonEmptyStr = None
    payment_unit: NonEmptyStr = "item"
    patient_amount: float | None = Field(default=None, ge=0.0)
    effective_from: date | None = None
    effective_to: date | None = None
    restriction_text: OptionalNonEmptyStr = None
    setting: OptionalNonEmptyStr = None
    professional_component: bool | None = None
    facility_component: bool | None = None
    provenance: ProvenanceRecord

    @field_validator("currency")
    @classmethod
    def normalise_currency(cls, value: str | None) -> str | None:
        """Normalise currency codes to uppercase ISO-like strings."""
        return value.upper() if value is not None else None


class CoverageDecisionRecord(FrozenModel):
    """Normalised coverage or HTA decision metadata."""

    source_id: SourceId
    decision_id: NonEmptyStr
    jurisdiction: NonEmptyStr
    technology_name: NonEmptyStr
    technology_domain: NonEmptyStr
    decision_status: Literal[
        "covered",
        "covered_with_restrictions",
        "not_covered",
        "deferred",
        "under_review",
        "unknown",
    ]
    decision_date: date | None = None
    evidence_standard: OptionalNonEmptyStr = None
    restriction_summary: OptionalNonEmptyStr = None
    economic_notes: OptionalNonEmptyStr = None
    provenance: ProvenanceRecord


class CrosswalkCandidate(FrozenModel):
    """Candidate mapping between two reimbursement items or terminology codes."""

    left_source_id: SourceId
    right_source_id: SourceId
    left_code: NonEmptyStr
    right_code: NonEmptyStr
    relationship: CrosswalkRelationship
    confidence: Confidence
    evidence_methods: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    reviewer_status: Literal["unreviewed", "machine_reviewed", "clinician_reviewed", "rejected"] = (
        "unreviewed"
    )
    notes: OptionalNonEmptyStr = None

    @field_validator("evidence_methods", mode="before")
    @classmethod
    def tuplefy_methods(cls, value: object) -> tuple[str, ...]:
        """Convert list-like method fields into immutable tuples."""
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,)
        if isinstance(value, (list, tuple, set, frozenset)):
            return tuple(str(item).strip() for item in cast("Iterable[object]", value))
        return (str(value).strip(),)

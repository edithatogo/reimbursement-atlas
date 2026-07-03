"""Typed registry models for public reimbursement schedules and analyses."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import Annotated, Literal, cast

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

NonEmptyStr = Annotated[str, Field(min_length=1)]
SourceId = Annotated[str, Field(pattern=r"^[a-z0-9_]+$")]


class FrozenModel(BaseModel):
    """Strict immutable base model."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class SourceRecord(FrozenModel):
    """A public reimbursement schedule or contextual data source."""

    id: SourceId
    jurisdiction: NonEmptyStr
    system: NonEmptyStr
    schedule: NonEmptyStr
    domain: NonEmptyStr
    access_tier: Literal["tier_1", "tier_2", "tier_3"]
    format: NonEmptyStr
    primary_url: HttpUrl
    licence_notes: NonEmptyStr
    reliability: Literal["low", "medium", "high"]
    machine_readable: bool
    historical_versions: bool
    utilisation_data: bool
    refresh_cadence: NonEmptyStr
    data_owner: NonEmptyStr
    tags: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    notes: NonEmptyStr

    @field_validator("tags", mode="before")
    @classmethod
    def normalise_tags(cls, value: object) -> tuple[str, ...]:
        """Convert list-like tag data to a deterministic tuple."""
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,)
        if isinstance(value, (list, tuple, set, frozenset)):
            return tuple(str(item).strip() for item in cast("Iterable[object]", value))
        return (str(value).strip(),)


class SourceVersionRecord(FrozenModel):
    """A specific retrievable source version or fixture target."""

    id: SourceId
    source_id: SourceId
    version_label: NonEmptyStr
    source_url: HttpUrl
    format: NonEmptyStr
    parser_status: Literal["planned", "stubbed", "prototype", "validated", "production"]
    effective_from: date | None = None
    effective_to: date | None = None
    retrieved_at: NonEmptyStr | None = None
    checksum_sha256: NonEmptyStr | None = None
    notes: NonEmptyStr


class AnalysisRecord(FrozenModel):
    """A planned policy analysis using one or more sources."""

    id: SourceId
    title: NonEmptyStr
    purpose: NonEmptyStr
    difficulty: Literal["low", "medium", "high"]
    policy_insight: NonEmptyStr
    required_sources: tuple[SourceId, ...]
    primary_output: NonEmptyStr
    methods: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    caveats: NonEmptyStr
    stage: Literal["design", "prototype", "production"] = "design"

    @field_validator("required_sources", "methods", mode="before")
    @classmethod
    def tuplefy(cls, value: object) -> tuple[str, ...]:
        """Convert list-like fields to tuples."""
        if isinstance(value, str):
            return (value,)
        if isinstance(value, (list, tuple, set, frozenset)):
            return tuple(str(item).strip() for item in cast("Iterable[object]", value))
        return (str(value).strip(),)


class OntologyRecord(FrozenModel):
    """Ontology, classification, or terminology that may enrich mappings."""

    id: SourceId
    name: NonEmptyStr
    domain: NonEmptyStr
    licence_risk: NonEmptyStr
    repo_strategy: NonEmptyStr
    mapping_use: NonEmptyStr


class SourceStatusRecord(FrozenModel):
    """Current public-source observation used to prioritise acquisition."""

    id: SourceId
    source_id: SourceId
    observed_at: NonEmptyStr
    status_label: NonEmptyStr
    evidence_url: HttpUrl
    evidence_note: NonEmptyStr
    recommended_action: NonEmptyStr
    retrieval_priority: int = Field(ge=1, le=5)


class AnalysisRecipeRecord(FrozenModel):
    """Machine-readable analysis recipe for workflow planning and GitHub issues."""

    id: SourceId
    analysis_id: SourceId
    status: Literal["design", "prototype", "blocked", "production"]
    required_tables: tuple[NonEmptyStr, ...]
    output_tables: tuple[NonEmptyStr, ...]
    quality_gates: tuple[NonEmptyStr, ...]
    policy_question: NonEmptyStr
    caveats: NonEmptyStr

    @field_validator("required_tables", "output_tables", "quality_gates", mode="before")
    @classmethod
    def tuplefy_recipe_fields(cls, value: object) -> tuple[str, ...]:
        """Convert list-like recipe fields to tuples."""
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,)
        if isinstance(value, (list, tuple, set, frozenset)):
            return tuple(str(item).strip() for item in cast("Iterable[object]", value))
        return (str(value).strip(),)

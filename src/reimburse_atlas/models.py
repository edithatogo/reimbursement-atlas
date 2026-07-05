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


class SourceFileRecord(FrozenModel):
    """Exact file, endpoint or landing page needed for a source-version acquisition."""

    id: SourceId
    source_id: SourceId
    source_version_id: SourceId
    file_label: NonEmptyStr
    file_name: NonEmptyStr
    source_url: HttpUrl
    file_role: Literal[
        "primary",
        "supplementary",
        "landing_page",
        "licence_gate",
        "api_endpoint",
    ]
    expected_format: NonEmptyStr
    acquisition_mode: Literal[
        "manual_download",
        "manual_extract",
        "api_rate_limited",
        "landing_page_review",
        "licence_clickthrough_manual",
    ]
    licence_gate: Literal[
        "permissive_candidate",
        "public_reuse_review",
        "restricted_or_licence_review",
        "metadata_only",
    ]
    parser_hint: NonEmptyStr
    expected_record_count: int | None = Field(default=None, ge=0)
    current_observation: NonEmptyStr
    notes: NonEmptyStr


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


class ConductorTrackRecord(FrozenModel):
    """Machine-readable Conductor implementation track for GitHub Projects and agents."""

    id: SourceId
    title: NonEmptyStr
    phase: NonEmptyStr
    workstream: NonEmptyStr
    priority: Literal["must", "should", "could", "wont"]
    goal: NonEmptyStr
    deliverables: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    depends_on: tuple[SourceId, ...] = Field(default_factory=tuple)
    github_project_status: NonEmptyStr
    notes: NonEmptyStr

    @field_validator("deliverables", "depends_on", mode="before")
    @classmethod
    def tuplefy_track_fields(cls, value: object) -> tuple[str, ...]:
        """Convert list-like track fields to tuples."""
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,)
        if isinstance(value, (list, tuple, set, frozenset)):
            return tuple(str(item).strip() for item in cast("Iterable[object]", value))
        return (str(value).strip(),)


class RoadmapFunctionRecord(FrozenModel):
    """Planned function, command, service or workflow tracked to implementation."""

    id: SourceId
    track_id: SourceId
    name: NonEmptyStr
    interface: Literal[
        "cli", "api", "mcp", "dashboard", "data_pipeline", "github_action", "mojo_kernel"
    ]
    status: Literal["planned", "prototype", "blocked", "implemented", "deferred"]
    priority: Literal["must", "should", "could", "wont"]
    description: NonEmptyStr
    inputs: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    outputs: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    quality_gates: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    github_issue_title: NonEmptyStr

    @field_validator("inputs", "outputs", "quality_gates", mode="before")
    @classmethod
    def tuplefy_function_fields(cls, value: object) -> tuple[str, ...]:
        """Convert list-like function fields to tuples."""
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,)
        if isinstance(value, (list, tuple, set, frozenset)):
            return tuple(str(item).strip() for item in cast("Iterable[object]", value))
        return (str(value).strip(),)


class DatasetCandidateRecord(FrozenModel):
    """Dataset, schedule, registry or contextual corpus proposed for the atlas."""

    id: SourceId
    jurisdiction: NonEmptyStr
    name: NonEmptyStr
    domain: NonEmptyStr
    source_url: HttpUrl
    access_mode: Literal[
        "api",
        "curl_download",
        "wget_download",
        "manual_clickthrough",
        "landing_page",
        "local_licence_only",
    ]
    priority: Literal["must", "should", "could", "watch"]
    licence_gate: Literal[
        "permissive_candidate",
        "public_reuse_review",
        "restricted_or_licence_review",
        "metadata_only",
    ]
    parser_status: Literal["planned", "prototype", "blocked", "validated"]
    recommended_next_step: NonEmptyStr
    notes: NonEmptyStr


class MappingResourceRecord(FrozenModel):
    """Ontology, terminology, crosswalk or code-system mapping resource."""

    id: SourceId
    name: NonEmptyStr
    domain: NonEmptyStr
    source_url: HttpUrl
    access_mode: Literal["api", "download", "local_licence_only", "manual_review"]
    licence_gate: Literal[
        "permissive_candidate",
        "public_reuse_review",
        "restricted_or_licence_review",
        "metadata_only",
    ]
    local_only: bool
    priority: Literal["must", "should", "could", "watch"]
    mapping_strategy: NonEmptyStr
    notes: NonEmptyStr


class ResearchQuestionRecord(FrozenModel):
    """Pre-specified policy research question with protocol and output anchors."""

    id: SourceId
    track_id: SourceId
    question: NonEmptyStr
    protocol_path: NonEmptyStr
    report_path: NonEmptyStr
    required_datasets: tuple[SourceId, ...] = Field(default_factory=tuple)
    methods: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    outputs: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    osf_component: NonEmptyStr
    preregistration_status: Literal["planned", "drafted", "registered", "not_applicable"]

    @field_validator("required_datasets", "methods", "outputs", mode="before")
    @classmethod
    def tuplefy_research_fields(cls, value: object) -> tuple[str, ...]:
        """Convert list-like research fields to tuples."""
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,)
        if isinstance(value, (list, tuple, set, frozenset)):
            return tuple(str(item).strip() for item in cast("Iterable[object]", value))
        return (str(value).strip(),)


class OutputArtifactPlanRecord(FrozenModel):
    """Planned publication, dashboard, dataset, report or archive output."""

    id: SourceId
    track_id: SourceId
    output_type: Literal[
        "dataset",
        "dashboard",
        "protocol",
        "report",
        "preprint",
        "api",
        "mcp",
        "archive",
        "package",
    ]
    target_platform: Literal[
        "github", "huggingface_dataset", "huggingface_space", "osf", "zenodo", "local"
    ]
    path: NonEmptyStr
    status: Literal["planned", "drafted", "blocked", "implemented", "published"]
    release_gate: NonEmptyStr
    notes: NonEmptyStr


class RuntimeTargetRecord(FrozenModel):
    """Runtime, language or toolchain target used by local/CI gates."""

    id: SourceId
    name: NonEmptyStr
    version_target: NonEmptyStr
    role: NonEmptyStr
    installation_status: Literal["installed", "blocked_network", "missing", "wrong_tool", "planned"]
    local_status: NonEmptyStr
    ci_status: NonEmptyStr
    notes: NonEmptyStr


class ProtocolStatusRecord(FrozenModel):
    """Generated protocol/report completeness status for an OSF-aligned question."""

    id: SourceId
    research_question_id: SourceId
    protocol_path: NonEmptyStr
    report_path: NonEmptyStr
    protocol_exists: bool
    report_exists: bool
    required_section_count: int = Field(ge=0)
    present_section_count: int = Field(ge=0)
    missing_sections: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    protocol_word_count: int = Field(ge=0)
    report_word_count: int = Field(ge=0)
    completeness_score: float = Field(ge=0.0, le=1.0)
    osf_ready: bool
    recommended_next_step: NonEmptyStr

    @field_validator("missing_sections", mode="before")
    @classmethod
    def tuplefy_missing_sections(cls, value: object) -> tuple[str, ...]:
        """Convert list-like missing sections to tuples."""
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,) if value else ()
        if isinstance(value, (list, tuple, set, frozenset)):
            return tuple(str(item).strip() for item in cast("Iterable[object]", value))
        return (str(value).strip(),)


class DataAcquisitionAttemptRecord(FrozenModel):
    """One attempted curl/wget/API acquisition of a registered source file."""

    id: SourceId
    source_file_id: SourceId
    attempted_at: NonEmptyStr
    method: Literal["curl", "wget", "httpx", "api", "manual"]
    target_path: NonEmptyStr
    status: Literal[
        "downloaded", "blocked_network", "failed", "skipped_licence_gate", "not_attempted"
    ]
    exit_code: int | None = None
    bytes_downloaded: int = Field(default=0, ge=0)
    command: NonEmptyStr
    error_summary: NonEmptyStr

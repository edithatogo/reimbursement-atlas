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
    auth_env_var: NonEmptyStr | None = None


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
        "downloaded",
        "local_cache_available",
        "blocked_network",
        "blocked_secret",
        "failed",
        "skipped_licence_gate",
        "not_attempted",
    ]
    exit_code: int | None = None
    bytes_downloaded: int = Field(default=0, ge=0)
    command: NonEmptyStr
    error_summary: NonEmptyStr


class SourceContentValidationRecord(FrozenModel):
    """Generated validation status for a downloaded or licence-gated source file."""

    id: SourceId
    source_file_id: SourceId
    source_id: SourceId
    source_version_id: SourceId
    validation_status: Literal["pass", "warn", "fail", "missing", "skipped"]
    expected_format: NonEmptyStr
    expected_record_count: int | None = Field(default=None, ge=0)
    observed_record_count: int | None = Field(default=None, ge=0)
    byte_size: int = Field(default=0, ge=0)
    checksum_sha256: NonEmptyStr | None = None
    local_target_ref: NonEmptyStr
    issues: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    recommended_action: NonEmptyStr

    @field_validator("issues", mode="before")
    @classmethod
    def tuplefy_issues(cls, value: object) -> tuple[str, ...]:
        """Convert list-like issue fields into immutable tuples."""
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,) if value else ()
        if isinstance(value, (list, tuple, set, frozenset)):
            return tuple(str(item).strip() for item in cast("Iterable[object]", value))
        return (str(value).strip(),)


class DataQualityCheckRecord(FrozenModel):
    """Generated table-level data quality check for seed and derived artefacts."""

    id: SourceId
    table_name: NonEmptyStr
    check_name: NonEmptyStr
    severity: Literal["blocking", "advisory"]
    status: Literal["pass", "warn", "fail", "missing"]
    observed_value: NonEmptyStr
    expected_value: NonEmptyStr
    evidence_path: NonEmptyStr
    recommended_action: NonEmptyStr


class ResearchLinkageRecord(FrozenModel):
    """Generated linkage between a research question, sources/datasets, mappings and outputs."""

    id: SourceId
    research_question_id: SourceId
    track_id: SourceId
    linked_entity_type: Literal["source", "dataset_candidate", "mapping_resource", "output"]
    linked_entity_id: SourceId
    linked_entity_label: NonEmptyStr
    linkage_role: NonEmptyStr
    readiness_status: Literal["available", "planned", "blocked", "missing", "local_only"]
    recommended_action: NonEmptyStr


class DataDictionaryRecord(FrozenModel):
    """Generated data dictionary entry for one public/derived table artefact."""

    id: SourceId
    table_name: NonEmptyStr
    relative_path: NonEmptyStr
    file_format: NonEmptyStr
    row_count: int = Field(ge=0)
    column_count: int = Field(ge=0)
    columns: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    publication_scope: NonEmptyStr
    licence_gate: NonEmptyStr
    notes: NonEmptyStr

    @field_validator("columns", mode="before")
    @classmethod
    def tuplefy_columns(cls, value: object) -> tuple[str, ...]:
        """Convert list-like column fields into tuples."""
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,) if value else ()
        if isinstance(value, (list, tuple, set, frozenset)):
            return tuple(str(item).strip() for item in cast("Iterable[object]", value))
        return (str(value).strip(),)


class EvidenceReadinessRecord(FrozenModel):
    """Generated readiness status for one protocolled research question."""

    id: SourceId
    research_question_id: SourceId
    track_id: SourceId
    protocol_score: float = Field(ge=0.0, le=1.0)
    dataset_linkage_count: int = Field(ge=0)
    available_linkage_count: int = Field(ge=0)
    planned_linkage_count: int = Field(ge=0)
    blocked_linkage_count: int = Field(ge=0)
    missing_linkage_count: int = Field(ge=0)
    mapping_resource_count: int = Field(ge=0)
    output_plan_count: int = Field(ge=0)
    data_quality_blockers: int = Field(ge=0)
    source_validation_blockers: int = Field(ge=0)
    readiness_score: float = Field(ge=0.0, le=1.0)
    readiness_stage: Literal["blocked", "design", "prototype_ready", "evidence_ready"]
    recommended_action: NonEmptyStr


class SourceDriftRecord(FrozenModel):
    """Generated schema and row-count drift status for two tabular artefacts."""

    id: SourceId
    left_label: NonEmptyStr
    right_label: NonEmptyStr
    left_path: NonEmptyStr
    right_path: NonEmptyStr
    status: Literal["pass", "warn", "fail", "missing"]
    left_row_count: int | None = Field(default=None, ge=0)
    right_row_count: int | None = Field(default=None, ge=0)
    row_count_delta: int | None = None
    row_count_delta_pct: float | None = None
    added_columns: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    removed_columns: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    left_checksum_sha256: NonEmptyStr | None = None
    right_checksum_sha256: NonEmptyStr | None = None
    recommended_action: NonEmptyStr

    @field_validator("added_columns", "removed_columns", mode="before")
    @classmethod
    def tuplefy_drift_columns(cls, value: object) -> tuple[str, ...]:
        """Convert list-like drift column fields into tuples."""
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,) if value else ()
        if isinstance(value, (list, tuple, set, frozenset)):
            return tuple(str(item).strip() for item in cast("Iterable[object]", value))
        return (str(value).strip(),)


class SourceContractValidationRecord(FrozenModel):
    """Generated source-specific contract validation for reviewed local files."""

    id: SourceId
    source_file_id: SourceId
    source_id: SourceId
    source_version_id: SourceId
    parser_hint: NonEmptyStr
    contract_name: NonEmptyStr
    contract_status: Literal["pass", "warn", "fail", "missing", "skipped"]
    required_markers: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    observed_markers: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    expected_columns: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    observed_columns: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    byte_size: int = Field(default=0, ge=0)
    issues: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    recommended_action: NonEmptyStr

    @field_validator(
        "required_markers",
        "observed_markers",
        "expected_columns",
        "observed_columns",
        "issues",
        mode="before",
    )
    @classmethod
    def tuplefy_contract_fields(cls, value: object) -> tuple[str, ...]:
        """Convert list-like contract fields into tuples."""
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,) if value else ()
        if isinstance(value, (list, tuple, set, frozenset)):
            return tuple(str(item).strip() for item in cast("Iterable[object]", value))
        return (str(value).strip(),)


class GitHubProjectItemRecord(FrozenModel):
    """Generated GitHub Project item import row for issue/project creation."""

    id: SourceId
    item_type: Literal["issue", "epic", "milestone", "track", "release_gate"]
    title: NonEmptyStr
    body_path: NonEmptyStr
    epic_id: NonEmptyStr
    epic_title: NonEmptyStr
    track_id: SourceId | None = None
    status: Literal["todo", "ready", "blocked", "done"]
    priority: Literal["must", "should", "could", "wont", "unknown"]
    labels: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    milestone: NonEmptyStr
    project_view: NonEmptyStr
    recommended_action: NonEmptyStr

    @field_validator("labels", mode="before")
    @classmethod
    def tuplefy_labels(cls, value: object) -> tuple[str, ...]:
        """Convert list-like labels into tuples."""
        if value is None:
            return ()
        if isinstance(value, str):
            return tuple(part.strip() for part in value.split(",") if part.strip())
        if isinstance(value, (list, tuple, set, frozenset)):
            return tuple(str(item).strip() for item in cast("Iterable[object]", value))
        return (str(value).strip(),)


class FinalHandoffTaskRecord(FrozenModel):
    """Generated task that remains for a network-enabled or credentialed environment."""

    id: SourceId
    conductor_track: NonEmptyStr
    github_issues: tuple[int, ...] = ()
    task_group: Literal[
        "source_ingestion",
        "security",
        "publication",
        "release",
        "research",
        "automation",
        "mappings",
    ]
    title: NonEmptyStr
    status: Literal[
        "ready_local",
        "partial",
        "blocked_network",
        "blocked_secret",
        "blocked_review",
        "complete",
    ]
    required_environment: NonEmptyStr
    command: NonEmptyStr
    evidence_path: NonEmptyStr
    unblock_condition: NonEmptyStr
    recommended_action: NonEmptyStr

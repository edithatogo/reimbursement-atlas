"""Fail-closed contracts for medallion evidence and promotion boundaries."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, HttpUrl, model_validator

from reimburse_atlas.models import FrozenModel, NonEmptyStr, SourceId

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
MedallionLayer = Literal["bronze_b0", "bronze_b1", "bronze_b2", "silver", "gold", "platinum"]
RightsState = Literal[
    "permissive",
    "public_reuse_review",
    "restricted_local_only",
    "metadata_only",
]


class BronzeSourceIndexRecord(FrozenModel):
    """B0 source identity; indexing never implies acquisition or coverage."""

    source_id: SourceId
    source_version_id: SourceId
    authoritative_locator: HttpUrl
    expected_media_types: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    rights_state: RightsState
    credential_state: Literal["none", "required", "unknown"]
    indexed_at: NonEmptyStr
    acquisition_status: Literal["not_attempted", "attempted", "acquired", "unavailable"]
    notes: NonEmptyStr


class BronzeAcquisitionReceipt(FrozenModel):
    """B1 append-only acquisition event and admission metadata."""

    event_id: NonEmptyStr
    acquisition_id: NonEmptyStr
    source_id: SourceId
    source_version_id: SourceId
    source_locator: HttpUrl
    retrieved_at: NonEmptyStr
    source_published_at: NonEmptyStr | None = None
    payload_sha256: Sha256 | None = None
    byte_size: int | None = Field(default=None, ge=0)
    media_type: NonEmptyStr | None = None
    outcome: Literal["acquired", "metadata_observed", "blocked", "failed"]
    rights_state: RightsState
    admission_state: Literal["pending", "admitted", "quarantined", "rejected"]
    evidence_disposition: Literal["retained_bytes", "rights_constrained_reference", "none"]
    predecessor_event_sha256: Sha256 | None = None
    notes: NonEmptyStr

    @model_validator(mode="after")
    def require_payload_identity_for_acquisition(self) -> BronzeAcquisitionReceipt:
        """Require exact payload identity whenever bytes were acquired or retained."""
        if self.outcome == "acquired" and self.payload_sha256 is None:
            message = "acquired events require payload_sha256"
            raise ValueError(message)
        if self.evidence_disposition == "retained_bytes" and (
            self.payload_sha256 is None or self.byte_size is None
        ):
            message = "retained bytes require payload_sha256 and byte_size"
            raise ValueError(message)
        if self.outcome != "acquired" and self.evidence_disposition == "retained_bytes":
            message = "retained bytes require an acquired outcome"
            raise ValueError(message)
        return self


class BronzeEvidenceRecord(FrozenModel):
    """B2 immutable bytes or a rights-constrained immutable reference."""

    evidence_id: NonEmptyStr
    acquisition_id: NonEmptyStr
    source_id: SourceId
    source_version_id: SourceId
    evidence_kind: Literal["immutable_bytes", "rights_constrained_reference"]
    payload_sha256: Sha256
    byte_size: int = Field(ge=0)
    immutable_locator: NonEmptyStr
    source_locator: HttpUrl
    rights_state: RightsState
    fixity_verified_at: NonEmptyStr
    notes: NonEmptyStr

    @model_validator(mode="after")
    def enforce_rights_constrained_reference(self) -> BronzeEvidenceRecord:
        """Prevent restricted bytes from being represented as publishable evidence."""
        if (
            self.rights_state in {"restricted_local_only", "metadata_only"}
            and self.evidence_kind != "rights_constrained_reference"
        ):
            message = "restricted or metadata-only evidence must use an immutable reference"
            raise ValueError(message)
        return self


class MedallionArtifactRecord(FrozenModel):
    """Checksum-bound Silver, Gold, or Platinum artifact identity."""

    artifact_id: NonEmptyStr
    layer: Literal["silver", "gold", "platinum"]
    relative_path: NonEmptyStr
    sha256: Sha256
    contract_id: NonEmptyStr
    input_artifact_ids: tuple[NonEmptyStr, ...] = Field(min_length=1)
    input_sha256: tuple[Sha256, ...] = Field(min_length=1)
    generated_at: NonEmptyStr
    rights_state: RightsState
    promotion_status: Literal["candidate", "approved_within_scope", "blocked"]
    notes: NonEmptyStr

    @model_validator(mode="after")
    def reject_unsafe_paths(self) -> MedallionArtifactRecord:
        """Keep machine-local and raw-cache paths out of governed artifacts."""
        path = self.relative_path.replace("\\", "/")
        if path.startswith("/") or ".." in path.split("/"):
            message = "relative_path must be repository-relative"
            raise ValueError(message)
        if any(part in {"raw", "raw_live", "local", "cache"} for part in path.split("/")):
            message = "governed artifacts cannot point at raw or local caches"
            raise ValueError(message)
        return self


class MedallionPromotionDecision(FrozenModel):
    """Explicit, evidence-bound decision for one permitted layer transition."""

    decision_id: NonEmptyStr
    subject_id: NonEmptyStr
    from_layer: MedallionLayer
    to_layer: MedallionLayer
    input_sha256: tuple[Sha256, ...] = Field(min_length=1)
    required_gate_ids: tuple[NonEmptyStr, ...] = Field(min_length=1)
    passed_gate_ids: tuple[NonEmptyStr, ...] = Field(default_factory=tuple)
    status: Literal["approved", "blocked", "rejected"]
    decided_at: NonEmptyStr
    reason_codes: tuple[NonEmptyStr, ...] = Field(min_length=1)
    scope_notes: NonEmptyStr

    @model_validator(mode="after")
    def enforce_transition_and_gates(self) -> MedallionPromotionDecision:
        """Reject layer skipping and approvals with incomplete gates."""
        allowed = {
            ("bronze_b0", "bronze_b1"),
            ("bronze_b1", "bronze_b2"),
            ("bronze_b1", "silver"),
            ("bronze_b2", "silver"),
            ("silver", "gold"),
            ("gold", "platinum"),
        }
        if (self.from_layer, self.to_layer) not in allowed:
            message = "medallion layer skipping is prohibited"
            raise ValueError(message)
        missing = set(self.required_gate_ids) - set(self.passed_gate_ids)
        if self.status == "approved" and missing:
            message = f"approved promotion has missing gates: {sorted(missing)}"
            raise ValueError(message)
        return self

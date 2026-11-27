"""Admit Casemix metadata references without granting publication authority."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Sequence
from datetime import datetime
from ipaddress import ip_address
from pathlib import Path
from typing import Annotated, Any, Literal
from urllib.parse import parse_qsl, urlsplit

from pydantic import Field, HttpUrl, model_validator

from reimburse_atlas.medallion import (
    BronzeAcquisitionReceipt,
    BronzeEvidenceRecord,
    BronzeSourceIndexRecord,
    MedallionArtifactRecord,
    MedallionPromotionDecision,
)
from reimburse_atlas.models import FrozenModel, SourceId

METADATA_NOTE = "Metadata-only handoff; no source payload included."
SCOPE_NOTE = "Metadata intake only; no public promotion authorized."
Token = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9_.:-]*$")]
GitCommit = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
UNSAFE_PATH_PARTS = frozenset({
    "raw",
    "raw_live",
    "private_raw",
    "restricted_derived",
    "private",
    "local",
    "cache",
    "scratch",
    "workspace",
})
SECRET_QUERY_KEYS = frozenset({
    "token",
    "access_token",
    "api_key",
    "key",
    "password",
    "signature",
    "sig",
    "x-amz-signature",
    "x-amz-credential",
})


def _require(condition: bool, message: str) -> None:
    """Raise a stable validation error for a failed intake invariant."""
    if not condition:
        raise ValueError(message)


def _unique(values: Sequence[object], kind: str) -> None:
    """Reject ambiguous identifiers before building lookup tables."""
    _require(len(values) == len(set(values)), f"duplicate {kind}")


def _timestamp(value: str) -> None:
    """Require a dated timestamp or date, without treating it as external evidence."""
    datetime.fromisoformat(value)


def _token(value: str) -> None:
    """Restrict identity fields to metadata tokens, not free-form source text."""
    _require(re.fullmatch(r"[a-z0-9][a-z0-9_.:-]*", value) is not None, "invalid metadata token")


def _provider_url(value: HttpUrl) -> None:
    """Reject credentials and local endpoints in provider metadata."""
    parts = urlsplit(str(value))
    _require(parts.username is None and parts.password is None, "provider URL has credentials")
    host = parts.hostname or ""
    _require(host != "localhost" and not host.endswith(".local"), "provider URL is local")
    try:
        address = ip_address(host)
    except ValueError:
        address = None
    _require(address is None or address.is_global, "provider URL is not public")
    _require(
        not any(key.casefold() in SECRET_QUERY_KEYS for key, _ in parse_qsl(parts.query)),
        "provider URL has a credential query",
    )


class CasemixSource(FrozenModel):
    """Provider URL identities only; no imported names or classification descriptors."""

    source_id: SourceId
    provider_urls: tuple[HttpUrl, ...] = Field(min_length=1)


class CasemixHandoff(FrozenModel):
    """Public-safe envelope reusing the repository's existing medallion contracts."""

    schema_version: Literal["casemix-atlas-handoff-v1"]
    source_release_id: Token
    source_commit: GitCommit
    generated_at: str
    sources: tuple[CasemixSource, ...] = Field(min_length=1)
    source_index: tuple[BronzeSourceIndexRecord, ...] = Field(min_length=1)
    acquisition_receipts: tuple[BronzeAcquisitionReceipt, ...] = ()
    evidence: tuple[BronzeEvidenceRecord, ...] = ()
    artifacts: tuple[MedallionArtifactRecord, ...] = ()
    promotion_decisions: tuple[MedallionPromotionDecision, ...] = ()

    @model_validator(mode="after")
    def validate_intake(self) -> CasemixHandoff:
        """Validate provenance, immutable references and the unapproved boundary."""
        _timestamp(self.generated_at)
        _validate_source_identity(self)
        _validate_acquisition(self)
        _validate_evidence(self)
        _validate_artifacts(self)
        _validate_decisions(self)
        return self


def _validate_source_identity(handoff: CasemixHandoff) -> None:
    """Bind every B0 source/version to an explicitly supplied provider URL."""
    _unique([row.source_id for row in handoff.sources], "source_id")
    _unique([(row.source_id, row.source_version_id) for row in handoff.source_index], "B0 version")
    providers = {row.source_id: {str(url) for url in row.provider_urls} for row in handoff.sources}
    _require(
        set(providers) == {row.source_id for row in handoff.source_index}, "source set mismatch"
    )
    for source in handoff.sources:
        _unique([str(url) for url in source.provider_urls], "provider URL")
        for url in source.provider_urls:
            _provider_url(url)
    for row in handoff.source_index:
        _require(
            str(row.authoritative_locator) in providers[row.source_id], "B0 provider URL mismatch"
        )
        _require(row.notes == METADATA_NOTE, "B0 notes must use the metadata-only statement")
        _timestamp(row.indexed_at)
        for media_type in row.expected_media_types:
            _require(
                re.fullmatch(r"[a-z0-9.+-]+/[a-z0-9.+-]+", media_type) is not None,
                "invalid media type",
            )


def _validate_acquisition(handoff: CasemixHandoff) -> None:
    """Check B1 identities while excluding any retained-byte transfer."""
    _unique([row.event_id for row in handoff.acquisition_receipts], "B1 event_id")
    _unique([row.acquisition_id for row in handoff.acquisition_receipts], "B1 acquisition_id")
    index = {(row.source_id, row.source_version_id): row for row in handoff.source_index}
    providers = {row.source_id: {str(url) for url in row.provider_urls} for row in handoff.sources}
    acquired: set[tuple[str, str]] = set()
    for row in handoff.acquisition_receipts:
        _token(row.event_id)
        _token(row.acquisition_id)
        _timestamp(row.retrieved_at)
        if row.source_published_at is not None:
            _timestamp(row.source_published_at)
        key = (row.source_id, row.source_version_id)
        _require(key in index, "B1 source/version mismatch")
        _require(row.rights_state == index[key].rights_state, "B1 rights mismatch")
        _require(str(row.source_locator) in providers[row.source_id], "B1 provider URL mismatch")
        _require(row.notes == METADATA_NOTE, "B1 notes must use the metadata-only statement")
        _require(
            row.evidence_disposition != "retained_bytes", "handoff cannot transfer retained bytes"
        )
        if row.outcome == "acquired":
            acquired.add(key)
            _require(row.byte_size is not None, "acquired metadata requires byte_size")
            _require(
                row.evidence_disposition == "rights_constrained_reference",
                "acquired metadata requires reference disposition",
            )
        if row.media_type is not None:
            _require(
                re.fullmatch(r"[a-z0-9.+-]+/[a-z0-9.+-]+", row.media_type) is not None,
                "invalid media type",
            )
    indexed_acquired = {key for key, row in index.items() if row.acquisition_status == "acquired"}
    _require(acquired == indexed_acquired, "B0/B1 acquisition status mismatch")


def _validate_evidence(handoff: CasemixHandoff) -> None:
    """Resolve every B2 reference to the exact acquired B1 bytes and source."""
    _unique([row.evidence_id for row in handoff.evidence], "B2 evidence_id")
    _unique([row.acquisition_id for row in handoff.evidence], "B2 acquisition_id")
    receipts = {row.acquisition_id: row for row in handoff.acquisition_receipts}
    for row in handoff.evidence:
        _token(row.evidence_id)
        _timestamp(row.fixity_verified_at)
        _require(row.notes == METADATA_NOTE, "B2 notes must use the metadata-only statement")
        _require(
            row.evidence_kind == "rights_constrained_reference",
            "handoff accepts B2 references only",
        )
        _require(
            row.immutable_locator == f"urn:sha256:{row.payload_sha256}",
            "B2 immutable locator/hash mismatch",
        )
        _require(row.acquisition_id in receipts, "B2 acquisition reference is missing")
        receipt = receipts[row.acquisition_id]
        _require(receipt.outcome == "acquired", "B2 requires an acquired B1 event")
        for field in (
            "source_id",
            "source_version_id",
            "payload_sha256",
            "byte_size",
            "source_locator",
            "rights_state",
        ):
            _require(getattr(row, field) == getattr(receipt, field), f"B2/B1 {field} mismatch")


def _validate_artifact_path(relative_path: str) -> None:
    """Reject machine paths, encoded paths and raw-cache references."""
    _require(re.fullmatch(r"[a-zA-Z0-9_./-]+", relative_path) is not None, "unsafe artifact path")
    parts = relative_path.split("/")
    _require(not any(part in {"", ".", ".."} for part in parts), "unsafe artifact path")
    _require(
        not ({part.casefold() for part in parts} & UNSAFE_PATH_PARTS), "restricted artifact path"
    )


def _validate_artifacts(handoff: CasemixHandoff) -> None:
    """Bind candidate artifact inputs to known checksums at the preceding layer."""
    _unique([row.artifact_id for row in handoff.artifacts], "artifact_id")
    _unique([row.relative_path for row in handoff.artifacts], "artifact path")
    identities = {
        row.acquisition_id: (row.payload_sha256, "bronze_b1")
        for row in handoff.acquisition_receipts
        if row.outcome == "acquired"
    }
    for row in handoff.evidence:
        _require(row.evidence_id not in identities, "ambiguous lineage identifier")
        identities[row.evidence_id] = (row.payload_sha256, "bronze_b2")
    for artifact in handoff.artifacts:
        _require(artifact.artifact_id not in identities, "ambiguous lineage identifier")
        identities[artifact.artifact_id] = (artifact.sha256, artifact.layer)
    allowed_inputs = {
        "silver": {"bronze_b1", "bronze_b2"},
        "gold": {"silver"},
        "platinum": {"gold"},
    }
    for artifact in handoff.artifacts:
        _token(artifact.artifact_id)
        _token(artifact.contract_id)
        _timestamp(artifact.generated_at)
        _validate_artifact_path(artifact.relative_path)
        _require(
            artifact.notes == METADATA_NOTE, "artifact notes must use the metadata-only statement"
        )
        _require(
            artifact.promotion_status != "approved_within_scope",
            "promotion requires a checksum-bound human decision outside this metadata intake",
        )
        _require(
            len(artifact.input_artifact_ids) == len(artifact.input_sha256),
            "artifact input ID/hash length mismatch",
        )
        _unique(artifact.input_artifact_ids, "artifact input")
        for input_id, checksum in zip(
            artifact.input_artifact_ids, artifact.input_sha256, strict=True
        ):
            _require(input_id in identities, "artifact input is missing")
            expected_hash, input_layer = identities[input_id]
            _require(checksum == expected_hash, "artifact input SHA-256 mismatch")
            _require(input_layer in allowed_inputs[artifact.layer], "artifact lineage skips layers")


def _validate_decisions(handoff: CasemixHandoff) -> None:
    """Keep candidate decisions blocked until the existing accountable review path."""
    _unique([row.decision_id for row in handoff.promotion_decisions], "decision_id")
    _unique([row.subject_id for row in handoff.promotion_decisions], "decision subject")
    artifacts = {row.artifact_id: row for row in handoff.artifacts}
    _require(
        set(artifacts) == {row.subject_id for row in handoff.promotion_decisions},
        "candidate decision set mismatch",
    )
    layers = {row.acquisition_id: "bronze_b1" for row in handoff.acquisition_receipts}
    layers.update({row.evidence_id: "bronze_b2" for row in handoff.evidence})
    layers.update({row.artifact_id: row.layer for row in handoff.artifacts})
    for decision in handoff.promotion_decisions:
        _token(decision.decision_id)
        _timestamp(decision.decided_at)
        _require(
            decision.scope_notes == SCOPE_NOTE,
            "decision scope must use the metadata-only statement",
        )
        _require(
            decision.status != "approved",
            "promotion requires a checksum-bound human decision outside this metadata intake",
        )
        artifact = artifacts[decision.subject_id]
        _require(decision.to_layer == artifact.layer, "decision target layer mismatch")
        _require(
            all(
                layers[input_id] == decision.from_layer for input_id in artifact.input_artifact_ids
            ),
            "decision source layer mismatch",
        )
        _require(decision.input_sha256 == artifact.input_sha256, "decision input SHA-256 mismatch")
        for value in (
            *decision.required_gate_ids,
            *decision.passed_gate_ids,
            *decision.reason_codes,
        ):
            _token(value)


def _unique_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate keys before JSON parsing can hide content or decisions."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def _parse_handoff(data: bytes) -> CasemixHandoff:
    """Validate the same immutable input bytes that an admission receipt hashes."""
    payload = json.loads(data, object_pairs_hook=_unique_json_keys)
    return CasemixHandoff.model_validate(payload)


def load_casemix_handoff(path: Path) -> CasemixHandoff:
    """Read and validate one handoff without changing registries or approvals."""
    return _parse_handoff(path.read_bytes())


def admit_casemix_handoff(path: Path) -> dict[str, object]:
    """Return metadata admission evidence, never a licence or publication receipt."""
    data = path.read_bytes()
    handoff = _parse_handoff(data)
    return {
        "schema_version": "casemix-atlas-admission-v1",
        "source_release_id": handoff.source_release_id,
        "source_commit": handoff.source_commit,
        "handoff_sha256": hashlib.sha256(data).hexdigest(),
        "status": "admitted_metadata_only",
        "counts": {
            "source_index": len(handoff.source_index),
            "acquisition_receipts": len(handoff.acquisition_receipts),
            "evidence": len(handoff.evidence),
            "artifacts": len(handoff.artifacts),
            "promotion_decisions": len(handoff.promotion_decisions),
        },
        "promotion_status": "blocked_pending_accountable_review",
        "raw_payloads_included": False,
        "human_approval_inferred": False,
        "source_authority_independently_verified": False,
    }

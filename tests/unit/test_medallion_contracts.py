"""Contract tests for medallion evidence and promotion boundaries."""

from __future__ import annotations

import pytest
from pydantic import HttpUrl, ValidationError

from reimburse_atlas.medallion import (
    BronzeAcquisitionReceipt,
    BronzeEvidenceRecord,
    MedallionArtifactRecord,
    MedallionPromotionDecision,
)


def test_retained_bronze_bytes_require_checksum_and_size() -> None:
    """B1 cannot claim retained bytes without exact identity."""
    with pytest.raises(ValidationError, match="payload_sha256 and byte_size"):
        BronzeAcquisitionReceipt(
            event_id="event-1",
            acquisition_id="acquisition-1",
            source_id="au_mbs",
            source_version_id="au_mbs_20260701",
            source_locator=HttpUrl("https://example.gov/source.xml"),
            retrieved_at="2026-08-25T00:00:00Z",
            outcome="acquired",
            rights_state="permissive",
            admission_state="admitted",
            evidence_disposition="retained_bytes",
            payload_sha256="a" * 64,
            notes="Test acquisition.",
        )


def test_restricted_bronze_evidence_requires_reference_semantics() -> None:
    """Restricted payloads cannot masquerade as publishable immutable bytes."""
    with pytest.raises(ValidationError, match="must use an immutable reference"):
        BronzeEvidenceRecord(
            evidence_id="evidence-1",
            acquisition_id="acquisition-1",
            source_id="us_cms_pfs",
            source_version_id="us_cms_pfs_2026",
            evidence_kind="immutable_bytes",
            payload_sha256="b" * 64,
            byte_size=10,
            immutable_locator="cas://sha256/bbbbb",
            source_locator=HttpUrl("https://example.gov/restricted.zip"),
            rights_state="restricted_local_only",
            fixity_verified_at="2026-08-25T00:00:00Z",
            notes="Reference-only publication boundary.",
        )


def test_governed_artifacts_reject_raw_cache_paths() -> None:
    """Silver and later manifests may not expose raw local paths."""
    with pytest.raises(ValidationError, match="raw or local caches"):
        MedallionArtifactRecord(
            artifact_id="silver-1",
            layer="silver",
            relative_path="data/raw_live/source.csv",
            sha256="c" * 64,
            contract_id="silver-source-faithful-v1",
            input_artifact_ids=("bronze-1",),
            input_sha256=("b" * 64,),
            generated_at="2026-08-25T00:00:00Z",
            rights_state="restricted_local_only",
            promotion_status="blocked",
            notes="Invalid raw path.",
        )


def test_promotion_rejects_layer_skipping() -> None:
    """Bronze evidence cannot be promoted directly to a public product."""
    with pytest.raises(ValidationError, match="layer skipping"):
        MedallionPromotionDecision(
            decision_id="decision-1",
            subject_id="bronze-1",
            from_layer="bronze_b2",
            to_layer="platinum",
            input_sha256=("d" * 64,),
            required_gate_ids=("rights",),
            passed_gate_ids=("rights",),
            status="approved",
            decided_at="2026-08-25T00:00:00Z",
            reason_codes=("scope_approved",),
            scope_notes="Invalid skipped transition.",
        )


def test_approved_promotion_requires_all_gates() -> None:
    """Approval is invalid while any declared gate is incomplete."""
    with pytest.raises(ValidationError, match="missing gates"):
        MedallionPromotionDecision(
            decision_id="decision-2",
            subject_id="silver-1",
            from_layer="silver",
            to_layer="gold",
            input_sha256=("e" * 64,),
            required_gate_ids=("rights", "mapping_review"),
            passed_gate_ids=("rights",),
            status="approved",
            decided_at="2026-08-25T00:00:00Z",
            reason_codes=("mapping_review_pending",),
            scope_notes="Fail closed until mapping review passes.",
        )

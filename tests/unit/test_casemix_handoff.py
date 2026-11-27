"""Integrity and public-boundary tests for Casemix metadata intake."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from reimburse_atlas.casemix_handoff import (
    METADATA_NOTE,
    SCOPE_NOTE,
    CasemixHandoff,
    admit_casemix_handoff,
    load_casemix_handoff,
)


@pytest.fixture
def handoff() -> dict[str, Any]:
    stamp = "2026-11-27T00:00:00Z"
    source = "test_source"
    version = "test_source_2025"
    url = "https://example.org/definitions.xlsx"
    rights = "restricted_local_only"
    payload: dict[str, Any] = {
        "schema_version": "casemix-atlas-handoff-v1",
        "source_release_id": "casemix-atlas-v0.2.0",
        "source_commit": "a" * 40,
        "generated_at": stamp,
        "sources": [{"source_id": source, "provider_urls": [url]}],
        "source_index": [
            {
                "source_id": source,
                "source_version_id": version,
                "authoritative_locator": url,
                "expected_media_types": ["application/zip"],
                "rights_state": rights,
                "credential_state": "none",
                "indexed_at": stamp,
                "acquisition_status": "acquired",
                "notes": METADATA_NOTE,
            }
        ],
        "acquisition_receipts": [
            {
                "event_id": "event-1",
                "acquisition_id": "acquisition-1",
                "source_id": source,
                "source_version_id": version,
                "source_locator": url,
                "retrieved_at": stamp,
                "payload_sha256": "b" * 64,
                "byte_size": 100,
                "media_type": "application/zip",
                "outcome": "acquired",
                "rights_state": rights,
                "admission_state": "quarantined",
                "evidence_disposition": "rights_constrained_reference",
                "notes": METADATA_NOTE,
            }
        ],
        "evidence": [
            {
                "evidence_id": "evidence-1",
                "acquisition_id": "acquisition-1",
                "source_id": source,
                "source_version_id": version,
                "evidence_kind": "rights_constrained_reference",
                "payload_sha256": "b" * 64,
                "byte_size": 100,
                "immutable_locator": "urn:sha256:" + "b" * 64,
                "source_locator": url,
                "rights_state": rights,
                "fixity_verified_at": stamp,
                "notes": METADATA_NOTE,
            }
        ],
        "artifacts": [],
        "promotion_decisions": [],
    }
    input_id, input_hash, previous_layer = "evidence-1", "b" * 64, "bronze_b2"
    for layer, char in [("silver", "c"), ("gold", "d"), ("platinum", "e")]:
        artifact_id = layer + "-candidate"
        payload["artifacts"].append({
            "artifact_id": artifact_id,
            "layer": layer,
            "relative_path": f"data/derived/casemix/{layer}.jsonl",
            "sha256": char * 64,
            "contract_id": "casemix-reference-v1",
            "input_artifact_ids": [input_id],
            "input_sha256": [input_hash],
            "generated_at": stamp,
            "rights_state": "metadata_only",
            "promotion_status": "candidate",
            "notes": METADATA_NOTE,
        })
        payload["promotion_decisions"].append({
            "decision_id": "decision-" + layer,
            "subject_id": artifact_id,
            "from_layer": previous_layer,
            "to_layer": layer,
            "input_sha256": [input_hash],
            "required_gate_ids": ["human_licence_review"],
            "passed_gate_ids": [],
            "status": "blocked",
            "decided_at": stamp,
            "reason_codes": ["new_source_scope_review_pending"],
            "scope_notes": SCOPE_NOTE,
        })
        input_id, input_hash, previous_layer = artifact_id, char * 64, layer
    return payload


def test_admission_preserves_unapproved_boundary(handoff, tmp_path: Path):
    path = tmp_path / "handoff.json"
    data = json.dumps(handoff).encode()
    path.write_bytes(data)
    report = admit_casemix_handoff(path)
    assert report["status"] == "admitted_metadata_only"
    assert report["handoff_sha256"] == hashlib.sha256(data).hexdigest()
    assert report["counts"]["artifacts"] == 3
    assert report["promotion_status"] == "blocked_pending_accountable_review"
    assert report["human_approval_inferred"] is False
    assert report["raw_payloads_included"] is False
    assert path.read_bytes() == data


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_id", "different_source"),
        ("source_version_id", "different_version"),
        ("byte_size", 101),
        ("source_locator", "https://example.org/other.xlsx"),
        ("rights_state", "permissive"),
    ],
)
def test_b2_must_match_acquired_source_identity(handoff, field, value):
    handoff["evidence"][0][field] = value
    with pytest.raises(ValidationError):
        CasemixHandoff.model_validate(handoff)


def test_b2_hash_cannot_be_changed_with_a_matching_fake_locator(handoff):
    handoff["evidence"][0]["payload_sha256"] = "f" * 64
    handoff["evidence"][0]["immutable_locator"] = "urn:sha256:" + "f" * 64
    with pytest.raises(ValueError, match="payload_sha256 mismatch"):
        CasemixHandoff.model_validate(handoff)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("immutable_locator", "file:///private/definitions.xlsx"),
        ("evidence_kind", "immutable_bytes"),
        ("notes", "Native classification descriptor carried in a note"),
        ("raw_payload", "source content"),
    ],
)
def test_reference_envelope_rejects_source_content(handoff, field, value):
    handoff["evidence"][0][field] = value
    with pytest.raises(ValidationError):
        CasemixHandoff.model_validate(handoff)


def test_b1_rejects_retained_byte_transfer(handoff):
    handoff["acquisition_receipts"][0]["evidence_disposition"] = "retained_bytes"
    with pytest.raises(ValueError, match="retained bytes"):
        CasemixHandoff.model_validate(handoff)


def test_b0_cannot_claim_unobserved_acquisition(handoff):
    handoff["acquisition_receipts"] = []
    with pytest.raises(ValueError, match="acquisition status mismatch"):
        CasemixHandoff.model_validate(handoff)


@pytest.mark.parametrize(
    "path",
    [
        "/absolute/source.jsonl",
        "C:/private/source.jsonl",
        "data/private_raw/source.jsonl",
        "data/derived/%2e%2e/source.jsonl",
        "data/../source.jsonl",
        "data/RAW/source.jsonl",
    ],
)
def test_artifact_paths_cannot_reveal_private_storage(handoff, path):
    handoff["artifacts"][0]["relative_path"] = path
    with pytest.raises(ValidationError):
        CasemixHandoff.model_validate(handoff)


def test_candidate_input_hash_is_checked(handoff):
    handoff["artifacts"][1]["input_sha256"] = ["f" * 64]
    with pytest.raises(ValueError, match="input SHA-256 mismatch"):
        CasemixHandoff.model_validate(handoff)


def test_candidate_inputs_cannot_skip_silver(handoff):
    handoff["artifacts"][1]["input_artifact_ids"] = ["evidence-1"]
    handoff["artifacts"][1]["input_sha256"] = ["b" * 64]
    with pytest.raises(ValueError, match="skips layers"):
        CasemixHandoff.model_validate(handoff)


def test_candidate_input_arrays_must_align(handoff):
    handoff["artifacts"][0]["input_sha256"].append("f" * 64)
    with pytest.raises(ValueError, match="length mismatch"):
        CasemixHandoff.model_validate(handoff)


def test_decision_is_bound_to_candidate_inputs(handoff):
    handoff["promotion_decisions"][0]["input_sha256"] = ["f" * 64]
    with pytest.raises(ValueError, match="decision input SHA-256 mismatch"):
        CasemixHandoff.model_validate(handoff)


def test_decision_cannot_misstate_input_layer(handoff):
    handoff["promotion_decisions"][0]["from_layer"] = "bronze_b1"
    with pytest.raises(ValueError, match="decision source layer mismatch"):
        CasemixHandoff.model_validate(handoff)


@pytest.mark.parametrize("kind", ["artifact", "decision"])
def test_automated_gate_passes_cannot_supply_human_approval(handoff, kind):
    if kind == "artifact":
        handoff["artifacts"][0]["promotion_status"] = "approved_within_scope"
    else:
        handoff["promotion_decisions"][0]["status"] = "approved"
        handoff["promotion_decisions"][0]["passed_gate_ids"] = ["human_licence_review"]
    with pytest.raises(ValueError, match="checksum-bound human decision"):
        CasemixHandoff.model_validate(handoff)


def test_human_decisions_cannot_be_self_attested_inside_handoff(handoff):
    handoff["human_decisions"] = [{"reviewer": "claimed reviewer", "decision": "approved"}]
    with pytest.raises(ValueError, match="Extra inputs"):
        CasemixHandoff.model_validate(handoff)


def test_candidate_needs_a_blocked_decision(handoff):
    handoff["promotion_decisions"].pop()
    with pytest.raises(ValueError, match="decision set mismatch"):
        CasemixHandoff.model_validate(handoff)


def test_duplicate_identity_is_rejected(handoff):
    handoff["source_index"].append(copy.deepcopy(handoff["source_index"][0]))
    with pytest.raises(ValueError, match="duplicate B0 version"):
        CasemixHandoff.model_validate(handoff)


def test_duplicate_json_keys_are_rejected_before_validation(tmp_path: Path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"sources": [], "sources": []}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate JSON key"):
        load_casemix_handoff(path)


@pytest.mark.parametrize(
    "url",
    [
        "https://user:password@example.org/file",
        "https://127.0.0.1/file",
        "https://example.org/file?access_token=secret",
    ],
)
def test_provider_metadata_excludes_private_or_credentialed_urls(handoff, url):
    handoff["sources"][0]["provider_urls"] = [url]
    with pytest.raises(ValidationError):
        CasemixHandoff.model_validate(handoff)


def test_catalogue_only_handoff_remains_unacquired(handoff):
    handoff["source_index"][0]["acquisition_status"] = "not_attempted"
    for field in ["acquisition_receipts", "evidence", "artifacts", "promotion_decisions"]:
        handoff[field] = []
    result = CasemixHandoff.model_validate(handoff)
    assert result.source_index[0].acquisition_status == "not_attempted"

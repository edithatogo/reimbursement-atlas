from __future__ import annotations

import json

import pytest

from reimburse_atlas.osf_registration import (
    apply_publication_decision,
    apply_registration_decision,
    build_registration_freeze,
    build_registration_review_packet,
    build_remote_registration_snapshot,
    check_registration_drift,
    registration_snapshot_sha256,
)
from reimburse_atlas.osf_sync import (
    OsfRemoteRecord,
    reconcile_osf_manifest,
    validate_osf_manifest_rows,
    validate_osf_remote_rows,
)


def _row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "id": "protocol",
        "local_path": "protocols/example.md",
        "osf_path": "/protocols/example.md",
        "exists": True,
        "byte_size": 10,
        "sha256": "abc",
        "publish_allowed": True,
    }
    row.update(overrides)
    return row


def test_reconciliation_is_idempotent_for_matching_remote_state() -> None:
    actions = reconcile_osf_manifest(
        [_row()],
        [OsfRemoteRecord("/protocols/example.md", "abc", 10)],
    )
    assert [(action.action, action.reason) for action in actions] == [
        ("skip", "checksum_and_size_match")
    ]


def test_reconciliation_plans_create_and_update() -> None:
    actions = reconcile_osf_manifest(
        [_row(), _row(id="report", osf_path="/reports/example.md", sha256="new")],
        [OsfRemoteRecord("/protocols/example.md", "old", 9)],
    )
    assert [action.action for action in actions] == ["update", "create"]


def test_reconciliation_blocks_unapproved_or_missing_rows() -> None:
    actions = reconcile_osf_manifest(
        [_row(publish_allowed=False), _row(id="missing", exists=False, osf_path="/missing")],
        [],
    )
    assert {action.reason for action in actions} == {"publish_not_allowed", "local_file_missing"}
    assert all(action.action == "blocked" for action in actions)


def test_publication_decision_requires_exact_current_checksum() -> None:
    digest = "a" * 64
    decision = {
        "status": "approved_within_scope",
        "approved_artifacts": [
            {"id": "protocol", "sha256": digest},
            {"id": "missing", "sha256": digest},
        ],
    }
    rows = apply_publication_decision(
        [
            _row(sha256=digest),
            _row(id="drift", sha256="b" * 64),
            _row(id="missing", sha256=digest, exists=False),
        ],
        decision,
    )
    assert [row["publish_allowed"] for row in rows] == [True, False, False]
    assert rows[0]["blocked_reason"] is None
    assert rows[1]["blocked_reason"]


def test_publication_decision_fails_closed_without_approval() -> None:
    rows = apply_publication_decision([_row(sha256="a" * 64)], None)
    assert rows[0]["publish_allowed"] is False


def test_registration_decision_applies_only_to_exact_freeze() -> None:
    freeze = {
        "protocol_digest": "a" * 64,
        "analysis_manifest_digest": "b" * 64,
        "proposed_source_cutoff": "2026-07-23T00:00:00Z",
        "source_cutoff": "not-frozen",
        "source_cutoff_status": "pending_accountable_approval",
        "review_approved": False,
        "status": "draft",
    }
    decision = {
        "status": "approved_for_registration",
        "protocol_digest": "a" * 64,
        "analysis_manifest_digest": "b" * 64,
        "source_cutoff": "2026-07-23T00:00:00Z",
        "reviewer": "owner",
        "reviewed_at": "2026-07-23T12:00:00Z",
    }
    approved = apply_registration_decision(freeze, decision)
    assert approved["review_approved"] is True
    assert approved["source_cutoff_status"] == "approved"
    assert approved["status"] == "approved_for_registration"

    stale = apply_registration_decision(
        {**freeze, "analysis_manifest_digest": "c" * 64},
        decision,
    )
    assert stale["review_approved"] is False
    assert stale["decision_reason"] == "registration_decision_drift:analysis_manifest_digest"


def test_reconciliation_prunes_only_managed_remote_rows() -> None:
    actions = reconcile_osf_manifest(
        [_row()],
        [
            OsfRemoteRecord("/old-managed", "old", 2, managed_by_manifest=True),
            OsfRemoteRecord("/unmanaged", "old", 2, managed_by_manifest=False),
        ],
        prune=True,
    )
    assert [(action.action, action.osf_path) for action in actions] == [
        ("delete", "/old-managed"),
        ("create", "/protocols/example.md"),
    ]


def test_manifest_validation_rejects_duplicates_traversal_and_bad_digest() -> None:
    errors = validate_osf_manifest_rows([
        _row(local_path="../secret", sha256="not-a-digest"),
        _row(id="duplicate", osf_path="/protocols/example.md"),
    ])
    assert "row 1: unsafe or invalid local_path" in errors
    assert "row 1: sha256 must be a lowercase SHA-256 digest" in errors
    assert "row 2: duplicate osf_path '/protocols/example.md'" in errors


def test_remote_validation_rejects_duplicate_and_unsafe_paths() -> None:
    errors = validate_osf_remote_rows([
        OsfRemoteRecord("/safe.md", "a" * 64, 1),
        OsfRemoteRecord("/safe.md", "a" * 64, 1),
        OsfRemoteRecord("/../escape", "a" * 64, 1),
    ])
    assert "row 2: duplicate osf_path '/safe.md'" in errors
    assert "row 3: unsafe or invalid osf_path" in errors


def _freeze(**overrides: object) -> dict[str, object]:
    freeze: dict[str, object] = {
        "protocol_digest": "protocol",
        "analysis_manifest_digest": "manifest",
        "source_cutoff": "2026-07-01",
        "review_approved": True,
    }
    freeze.update(overrides)
    return freeze


def _remote(**overrides: object) -> dict[str, object]:
    remote: dict[str, object] = {
        "schema_version": "osf-registration-snapshot-v1",
        "registration_id": "osf-reg-1",
        "registration_url": "https://osf.io/abc12/",
        "status": "registered",
        "submitted_at": "2026-07-16T00:00:00Z",
        "immutable": True,
        "protocol_digest": "protocol",
        "analysis_manifest_digest": "manifest",
        "source_cutoff": "2026-07-01",
    }
    remote.update(overrides)
    if "snapshot_sha256" not in overrides:
        remote["snapshot_sha256"] = registration_snapshot_sha256(remote)
    return remote


def test_registration_check_requires_remote_and_review() -> None:
    assert check_registration_drift(_freeze(), None)["status"] == "blocked"
    result = check_registration_drift(_freeze(review_approved=False), _remote())
    assert result["status"] == "blocked"
    assert result["reasons"] == ["human_review_not_approved"]


def test_registration_check_detects_fingerprint_drift() -> None:
    result = check_registration_drift(_freeze(), _remote(protocol_digest="changed"))
    assert result["status"] == "drift"
    assert result["reasons"] == ["registration_fingerprint_drift:protocol_digest"]


def test_registration_check_rejects_incomplete_remote_snapshot() -> None:
    remote = _remote()
    remote.pop("snapshot_sha256")
    result = check_registration_drift(_freeze(), remote)
    assert result["status"] == "blocked"
    assert result["reasons"] == ["invalid_remote_registration:snapshot_sha256"]


def test_registration_check_rejects_mismatched_snapshot_digest() -> None:
    remote = _remote()
    remote["source_cutoff"] = "2026-07-02"

    result = check_registration_drift(_freeze(), remote)

    assert result["status"] == "blocked"
    assert result["reasons"] == ["invalid_remote_registration:snapshot_sha256_mismatch"]


def test_registration_check_rejects_invalid_remote_metadata() -> None:
    remote = _remote(
        schema_version="wrong-schema",
        registration_id="",
        registration_url="https://example.invalid/registration",
        submitted_at="",
        immutable=False,
        snapshot_sha256="not-a-digest",
    )
    result = check_registration_drift(_freeze(), remote)
    assert result["status"] == "blocked"
    assert result["reasons"] == [
        (
            "invalid_remote_registration:schema_version,registration_id,registration_url,"
            "submitted_at,immutable,snapshot_sha256"
        )
    ]


def test_registration_check_accepts_matching_reviewed_registration() -> None:
    result = check_registration_drift(_freeze(), _remote())
    assert result["status"] == "ready"
    assert result["network_io"] is False
    assert result["mutation_performed"] is False


def test_build_remote_registration_snapshot_binds_receipt_to_freeze() -> None:
    receipt = {
        "schema_version": "osf-registration-receipt-v1",
        "registration_id": "abc12",
        "registration_url": "https://osf.io/abc12/",
        "registered_at": "2026-07-23T13:00:00Z",
        "public": True,
        "immutable": True,
        "status": "registered",
    }

    snapshot = build_remote_registration_snapshot(receipt, _freeze())

    assert snapshot["snapshot_sha256"] == registration_snapshot_sha256(snapshot)
    assert check_registration_drift(_freeze(), snapshot)["status"] == "ready"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("status", "pending_approval", "not active"),
        ("public", False, "public and immutable"),
        ("immutable", False, "public and immutable"),
    ],
)
def test_build_remote_registration_snapshot_rejects_unready_receipt(
    field: str,
    value: object,
    message: str,
) -> None:
    receipt: dict[str, object] = {
        "schema_version": "osf-registration-receipt-v1",
        "registration_id": "abc12",
        "registration_url": "https://osf.io/abc12/",
        "registered_at": "2026-07-23T13:00:00Z",
        "public": True,
        "immutable": True,
        "status": "registered",
    }
    receipt[field] = value

    with pytest.raises(ValueError, match=message):
        build_remote_registration_snapshot(receipt, _freeze())


def test_registration_review_packet_is_explicitly_unapproved(tmp_path) -> None:  # type: ignore[no-untyped-def]
    freeze = tmp_path / "freeze.json"
    freeze.write_text(
        json.dumps({
            "schema_version": "osf-registration-freeze-v1",
            "protocol_digest": "protocol",
            "analysis_manifest_digest": "manifest",
            "source_cutoff": "2026-07-01",
            "review_approved": False,
        }),
        encoding="utf-8",
    )
    protocols = tmp_path / "protocols.jsonl"
    protocols.write_text(
        json.dumps({"osf_ready": True}) + "\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text(json.dumps({"publish_allowed": False}) + "\n", encoding="utf-8")
    packet = build_registration_review_packet(
        freeze_path=freeze,
        protocol_status_path=protocols,
        sync_manifest_path=manifest,
    )
    assert "Decision: `blocked`" in packet
    assert "Temporal disclosure" in packet
    assert "must not describe those completed activities as preregistered" in packet
    assert "Protocols/reports OSF-ready: `1/1`" in packet
    assert "Manifest rows explicitly publishable: `0/1`" in packet
    assert "OSF metadata contract" in packet
    assert "accountable contributor list must be confirmed" in packet
    assert "exact checksum-bound rows" in packet


def test_registration_review_packet_records_scoped_approval(tmp_path) -> None:
    freeze = tmp_path / "freeze.json"
    freeze.write_text(
        json.dumps({
            "schema_version": "osf-registration-freeze-v1",
            "protocol_digest": "protocol",
            "analysis_manifest_digest": "manifest",
            "source_cutoff": "2026-07-23T00:00:00Z",
            "source_cutoff_status": "approved",
            "review_approved": True,
            "reviewer": "owner",
            "reviewed_at": "2026-07-23T12:00:00Z",
            "review_record": "data/osf_review/registration_decision.json",
        }),
        encoding="utf-8",
    )
    protocols = tmp_path / "protocols.jsonl"
    protocols.write_text(json.dumps({"osf_ready": True}) + "\n", encoding="utf-8")
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text(json.dumps({"publish_allowed": True}) + "\n", encoding="utf-8")

    packet = build_registration_review_packet(
        freeze_path=freeze,
        protocol_status_path=protocols,
        sync_manifest_path=manifest,
    )

    assert "Decision: `approved_for_registration`" in packet
    assert "- [x] Source cutoff and analysis manifest approved" in packet
    assert (
        "Papers, preprints, raw source payloads and restricted descriptors remain excluded."
        in packet
    )


def test_registration_freeze_exposes_proposed_cutoff_without_approval(tmp_path) -> None:  # type: ignore[no-untyped-def]
    (tmp_path / "protocols").mkdir()
    (tmp_path / "reports").mkdir()
    (tmp_path / "data/seed").mkdir(parents=True)
    (tmp_path / "data/seed/source_snapshots.jsonl").write_text(
        json.dumps({"retrieved_at": "2026-07-03T00:00:00Z"}) + "\n", encoding="utf-8"
    )
    (tmp_path / "data/seed/source_versions.jsonl").write_text(
        json.dumps({"retrieved_at": "2026-07-19T00:00:00Z"}) + "\n", encoding="utf-8"
    )
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text("{}\n", encoding="utf-8")

    freeze = build_registration_freeze(root=tmp_path, sync_manifest_path=manifest)

    assert freeze["proposed_source_cutoff"] == "2026-07-19T00:00:00Z"
    assert freeze["source_cutoff"] == "not-frozen"
    assert freeze["source_cutoff_status"] == "pending_accountable_approval"

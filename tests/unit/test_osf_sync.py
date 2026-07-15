from __future__ import annotations

from reimburse_atlas.osf_registration import check_registration_drift
from reimburse_atlas.osf_sync import OsfRemoteRecord, reconcile_osf_manifest


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
        "registration_id": "osf-reg-1",
        "status": "registered",
        "protocol_digest": "protocol",
        "analysis_manifest_digest": "manifest",
        "source_cutoff": "2026-07-01",
    }
    remote.update(overrides)
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


def test_registration_check_accepts_matching_reviewed_registration() -> None:
    result = check_registration_drift(_freeze(), _remote())
    assert result["status"] == "ready"
    assert result["network_io"] is False
    assert result["mutation_performed"] is False

from __future__ import annotations

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

"""Deterministic, fail-closed planning for OSF manifest reconciliation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SyncAction = Literal["blocked", "create", "update", "skip", "delete"]


@dataclass(frozen=True)
class OsfRemoteRecord:
    """Minimal remote state needed for checksum-based reconciliation."""

    osf_path: str
    sha256: str | None
    byte_size: int
    managed_by_manifest: bool = False


@dataclass(frozen=True)
class OsfReconciliationAction:
    """One explicit, non-mutating action proposed by the planner."""

    action: SyncAction
    manifest_id: str | None
    osf_path: str
    local_path: str | None
    reason: str


def reconcile_osf_manifest(
    local_rows: list[dict[str, object]],
    remote_rows: list[OsfRemoteRecord],
    *,
    prune: bool = False,
) -> list[OsfReconciliationAction]:
    """Compare a generated manifest with remote metadata without doing IO.

    Rows not explicitly marked ``publish_allowed`` are blocked. Pruning is
    opt-in and only considers remote records marked as managed by this
    manifest, preventing accidental deletion of unrelated OSF content.
    """
    remote_by_path = {row.osf_path: row for row in remote_rows}
    manifest_paths: set[str] = set()
    actions: list[OsfReconciliationAction] = []
    for row in local_rows:
        manifest_id = _text(row.get("id"))
        osf_path = _text(row.get("osf_path"))
        local_path = _text(row.get("local_path"))
        if not manifest_id or not osf_path:
            continue
        manifest_paths.add(osf_path)
        if row.get("publish_allowed") is not True:
            actions.append(
                OsfReconciliationAction(
                    "blocked", manifest_id, osf_path, local_path, "publish_not_allowed"
                )
            )
            continue
        if row.get("exists") is not True:
            actions.append(
                OsfReconciliationAction(
                    "blocked", manifest_id, osf_path, local_path, "local_file_missing"
                )
            )
            continue
        remote = remote_by_path.get(osf_path)
        if remote is None:
            action: SyncAction = "create"
            reason = "remote_path_missing"
        elif remote.sha256 == row.get("sha256") and remote.byte_size == row.get("byte_size"):
            action = "skip"
            reason = "checksum_and_size_match"
        else:
            action = "update"
            reason = "checksum_or_size_drift"
        actions.append(OsfReconciliationAction(action, manifest_id, osf_path, local_path, reason))

    if prune:
        for remote in remote_rows:
            if remote.managed_by_manifest and remote.osf_path not in manifest_paths:
                actions.append(
                    OsfReconciliationAction(
                        "delete", None, remote.osf_path, None, "managed_remote_not_in_manifest"
                    )
                )
    return sorted(actions, key=lambda action: (action.osf_path, action.action))


def _text(value: object) -> str | None:
    return value if isinstance(value, str) and value else None

"""Deterministic, fail-closed planning for OSF manifest reconciliation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Literal

SyncAction = Literal["blocked", "create", "update", "skip", "delete"]
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


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


def validate_osf_manifest_rows(rows: list[dict[str, object]]) -> list[str]:
    """Return deterministic schema and path errors for local manifest rows."""
    errors: list[str] = []
    ids: set[str] = set()
    paths: set[str] = set()
    for row_number, row in enumerate(rows, start=1):
        manifest_id = row.get("id")
        osf_path = row.get("osf_path")
        local_path = row.get("local_path")
        if not isinstance(manifest_id, str) or not manifest_id:
            errors.append(f"row {row_number}: id must be a non-empty string")
        elif manifest_id in ids:
            errors.append(f"row {row_number}: duplicate id {manifest_id!r}")
        else:
            ids.add(manifest_id)
        if not isinstance(osf_path, str) or not _safe_osf_path(osf_path):
            errors.append(f"row {row_number}: unsafe or invalid osf_path")
        elif osf_path in paths:
            errors.append(f"row {row_number}: duplicate osf_path {osf_path!r}")
        else:
            paths.add(osf_path)
        if not isinstance(local_path, str) or not _safe_local_path(local_path):
            errors.append(f"row {row_number}: unsafe or invalid local_path")
        byte_size = row.get("byte_size")
        if not isinstance(byte_size, int) or isinstance(byte_size, bool) or byte_size < 0:
            errors.append(f"row {row_number}: byte_size must be a non-negative integer")
        sha256 = row.get("sha256")
        if sha256 is not None and (
            not isinstance(sha256, str) or _SHA256_RE.fullmatch(sha256) is None
        ):
            errors.append(f"row {row_number}: sha256 must be a lowercase SHA-256 digest")
    return errors


def validate_osf_remote_rows(rows: list[OsfRemoteRecord]) -> list[str]:
    """Return deterministic schema and path errors for exported remote rows."""
    errors: list[str] = []
    paths: set[str] = set()
    for row_number, row in enumerate(rows, start=1):
        if not _safe_osf_path(row.osf_path):
            errors.append(f"row {row_number}: unsafe or invalid osf_path")
        elif row.osf_path in paths:
            errors.append(f"row {row_number}: duplicate osf_path {row.osf_path!r}")
        else:
            paths.add(row.osf_path)
        if row.byte_size < 0:
            errors.append(f"row {row_number}: byte_size must be non-negative")
        if row.sha256 is not None and _SHA256_RE.fullmatch(row.sha256) is None:
            errors.append(f"row {row_number}: sha256 must be a lowercase SHA-256 digest")
    return errors


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


def _safe_osf_path(value: str) -> bool:
    """Accept only normalized POSIX paths within the OSF project root."""
    path = PurePosixPath(value)
    return value.startswith("/") and value == path.as_posix() and ".." not in path.parts


def _safe_local_path(value: str) -> bool:
    """Accept only repository-relative POSIX paths, never absolute traversal paths."""
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and value == path.as_posix()


def _text(value: object) -> str | None:
    return value if isinstance(value, str) and value else None

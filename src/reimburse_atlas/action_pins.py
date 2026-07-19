"""GitHub Actions SHA-pin resolution helpers.

The resolver is deliberately non-mutating: it produces a reviewable table with the
current tag reference, resolved SHA when network is available, and the exact
`uses:` replacement string. Maintainers can apply the patch manually or wire a
future bot to consume the generated table.
"""

from __future__ import annotations

import string
import subprocess  # nosec B404
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from reimburse_atlas.automation import WorkflowUseRecord, scan_workflow_uses
from reimburse_atlas.toolchain import NETWORK_MARKERS

ResolutionStatus = Literal[
    "resolved",
    "skipped_sha",
    "skipped_local_or_docker",
    "blocked_network",
    "missing_tool",
    "failed",
]


@dataclass(frozen=True)
class ActionPinResolutionRecord:
    """Resolution result for one external action reference."""

    workflow: str
    line: int
    action: str
    ref: str
    current_uses: str
    status: ResolutionStatus
    resolved_sha: str | None
    suggested_uses: str | None
    notes: str

    def as_row(self) -> dict[str, object]:
        """Return a JSON/CSV-safe row."""
        return asdict(self)


def resolve_action_pin(  # ruff:ignore[too-many-return-statements]
    record: WorkflowUseRecord,
    *,
    timeout_seconds: int = 8,
) -> ActionPinResolutionRecord:
    """Resolve one action tag to an immutable SHA when possible."""
    if record.pin_class == "sha":
        return _record(record, "skipped_sha", None, "Already pinned to a full SHA.")
    if record.pin_class in {"local", "docker"}:
        return _record(
            record,
            "skipped_local_or_docker",
            None,
            "Local/docker reference does not need GitHub tag resolution.",
        )
    if not record.ref:
        return _record(record, "failed", None, "No ref component found in uses reference.")
    repo_url = f"https://github.com/{record.action}.git"
    candidates = (f"refs/tags/{record.ref}", record.ref)
    for candidate in candidates:
        try:
            completed = subprocess.run(  # nosec B603
                ("git", "ls-remote", repo_url, candidate),
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except FileNotFoundError:
            return _record(record, "missing_tool", None, "git executable is unavailable.")
        except subprocess.TimeoutExpired:
            return _record(record, "failed", None, "git ls-remote timed out.")
        combined = f"{completed.stdout}\n{completed.stderr}".lower()
        if completed.returncode != 0 and any(marker in combined for marker in NETWORK_MARKERS):
            return _record(
                record,
                "blocked_network",
                None,
                "Network/DNS blocked while resolving action tag.",
            )
        if completed.returncode != 0:
            continue
        sha = first_sha_from_ls_remote(completed.stdout)
        if sha is not None:
            return _record(record, "resolved", sha, "Resolved tag/ref to immutable commit SHA.")
    return _record(record, "failed", None, "Could not resolve ref through git ls-remote.")


def resolve_action_pins(root: Path) -> list[ActionPinResolutionRecord]:
    """Resolve all workflow action references from a repository root."""
    results: list[ActionPinResolutionRecord] = []
    network_blocked = False
    for record in scan_workflow_uses(root):
        if network_blocked and record.pin_class not in {"sha", "local", "docker"}:
            results.append(
                _record(
                    record,
                    "blocked_network",
                    None,
                    "Earlier action-pin lookup showed network/DNS was blocked.",
                )
            )
            continue
        result = resolve_action_pin(record)
        results.append(result)
        if result.status == "blocked_network":
            network_blocked = True
    return results


def _record(
    source: WorkflowUseRecord,
    status: ResolutionStatus,
    sha: str | None,
    notes: str,
) -> ActionPinResolutionRecord:
    suggested = f"{source.action}@{sha}" if sha is not None else None
    return ActionPinResolutionRecord(
        workflow=source.workflow,
        line=source.line,
        action=source.action,
        ref=source.ref,
        current_uses=source.uses,
        status=status,
        resolved_sha=sha,
        suggested_uses=suggested,
        notes=notes,
    )


def first_sha_from_ls_remote(stdout: str) -> str | None:
    """Extract the first 40-character SHA from git ls-remote output."""
    for line in stdout.splitlines():
        first = line.split(maxsplit=1)[0] if line.split() else ""
        if len(first) == 40 and all(char in string.hexdigits for char in first):
            return first.lower()
    return None

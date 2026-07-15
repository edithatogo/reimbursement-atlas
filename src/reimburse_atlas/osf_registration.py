"""Fail-closed OSF registration freeze and drift verification helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal, cast

RegistrationStatus = Literal["blocked", "drift", "ready"]


def build_registration_freeze(
    *, root: Path, sync_manifest_path: Path, source_cutoff: str = "not-frozen"
) -> dict[str, object]:
    """Build deterministic fingerprints for a future reviewed registration."""
    paths = sorted((*((root / "protocols").glob("*.md")), *((root / "reports").glob("*.md"))))
    return {
        "schema_version": "osf-registration-freeze-v1",
        "protocol_digest": _digest_paths(root, paths),
        "analysis_manifest_digest": _sha256_file(sync_manifest_path),
        "source_cutoff": source_cutoff,
        "review_approved": False,
        "registration_id": None,
        "status": "draft",
        "mutation_performed": False,
        "network_io": False,
    }


def check_registration_drift(
    freeze: dict[str, object], remote: dict[str, object] | None
) -> dict[str, object]:
    """Compare a local freeze with exported remote registration metadata."""
    status: RegistrationStatus = "blocked"
    reasons: list[str] = []
    required = ("protocol_digest", "analysis_manifest_digest", "source_cutoff")
    missing = [field for field in required if not isinstance(freeze.get(field), str)]
    if not isinstance(freeze.get("review_approved"), bool):
        missing.append("review_approved")
    if missing:
        reasons = ["invalid_freeze:" + ",".join(missing)]
    elif remote is None:
        reasons = ["remote_registration_snapshot_missing"]
    elif remote.get("status") not in {"registered", "embargoed"}:
        reasons = ["remote_registration_not_active"]
    elif (
        not isinstance(registration_id := remote.get("registration_id"), str) or not registration_id
    ):
        reasons = ["remote_registration_id_missing"]
    else:
        drift_fields = [field for field in required if remote.get(field) != freeze.get(field)]
        if drift_fields:
            status = "drift"
            reasons = ["registration_fingerprint_drift:" + ",".join(drift_fields)]
        elif freeze["review_approved"] is not True:
            reasons = ["human_review_not_approved"]
        else:
            status = "ready"
    return _result(status, reasons, freeze, remote)


def _result(
    status: RegistrationStatus,
    reasons: list[str],
    freeze: dict[str, object],
    remote: dict[str, object] | None,
) -> dict[str, object]:
    """Build a stable, non-mutating registration check result."""
    return {
        "schema_version": "osf-registration-check-v1",
        "status": status,
        "reasons": reasons,
        "registration_id": remote.get("registration_id") if remote else None,
        "local_protocol_digest": freeze.get("protocol_digest"),
        "local_analysis_manifest_digest": freeze.get("analysis_manifest_digest"),
        "remote_protocol_digest": remote.get("protocol_digest") if remote else None,
        "remote_analysis_manifest_digest": remote.get("analysis_manifest_digest")
        if remote
        else None,
        "network_io": False,
        "mutation_performed": False,
    }


def _digest_paths(root: Path, paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_registration_freeze(freeze: dict[str, object], path: Path) -> Path:
    """Write a deterministic registration freeze document."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def build_registration_review_packet(
    *,
    freeze_path: Path,
    protocol_status_path: Path,
    sync_manifest_path: Path,
) -> str:
    """Build a deterministic human-review packet without granting approval."""
    freeze = _read_object(freeze_path)
    protocol_rows = _read_jsonl(protocol_status_path)
    manifest_rows = _read_jsonl(sync_manifest_path)
    protocol_count = len(protocol_rows)
    complete_protocols = sum(row.get("osf_ready") is True for row in protocol_rows)
    allowed_rows = sum(row.get("publish_allowed") is True for row in manifest_rows)
    blocked_rows = len(manifest_rows) - allowed_rows
    lines = [
        "# OSF preregistration review packet",
        "",
        "This packet is a review aid, not an approval or registration submission.",
        "No network IO or remote mutation is performed by its generation.",
        "",
        "## Freeze",
        "",
        f"- Freeze schema: `{freeze.get('schema_version', 'unknown')}`",
        f"- Protocol digest: `{freeze.get('protocol_digest', 'missing')}`",
        f"- Analysis manifest digest: `{freeze.get('analysis_manifest_digest', 'missing')}`",
        f"- Source cutoff: `{freeze.get('source_cutoff', 'missing')}`",
        f"- Existing approval flag: `{freeze.get('review_approved', False)}`",
        "",
        "## Completeness",
        "",
        f"- Protocols/reports OSF-ready: `{complete_protocols}/{protocol_count}`",
        f"- Manifest rows explicitly publishable: `{allowed_rows}/{len(manifest_rows)}`",
        f"- Manifest rows still blocked: `{blocked_rows}`",
        "",
        "## Required human decisions",
        "",
        "- [ ] Methods review completed",
        "- [ ] Domain/clinical review completed",
        "- [ ] Source licence and derived-field review completed",
        "- [ ] Governance and publication review completed",
        "- [ ] Source cutoff and analysis manifest approved",
        "",
        "## Approval record",
        "",
        "- Reviewer(s):",
        "- Decision: `blocked`",
        "- Reviewed at:",
        "- Approval reference:",
        "",
        "The decision must be recorded by an accountable human reviewer before any",
        "sync-manifest row changes to `publish_allowed: true` or any registration",
        "submission is attempted.",
        "",
    ]
    return "\n".join(lines)


def write_registration_review_packet(content: str, path: Path) -> Path:
    """Write a deterministic registration review packet."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _read_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError
    return cast("dict[str, object]", payload)


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise TypeError
        rows.append(cast("dict[str, object]", payload))
    return rows

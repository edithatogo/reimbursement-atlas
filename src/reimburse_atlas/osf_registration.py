"""Fail-closed OSF registration freeze and drift verification helpers."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Literal, cast

RegistrationStatus = Literal["blocked", "drift", "ready"]
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def apply_publication_decision(
    manifest_rows: list[dict[str, object]], decision: dict[str, object] | None
) -> list[dict[str, object]]:
    """Authorize only exact checksum-bound OSF rows from an accountable decision."""
    approvals: dict[str, str] = {}
    if decision and decision.get("status") == "approved_within_scope":
        raw_approvals = decision.get("approved_artifacts")
        if isinstance(raw_approvals, list):
            for item in cast("list[object]", raw_approvals):
                if not isinstance(item, dict):
                    continue
                approval = cast("dict[str, object]", item)
                identifier = approval.get("id")
                sha256 = approval.get("sha256")
                if isinstance(identifier, str) and isinstance(sha256, str):
                    approvals[identifier] = sha256

    decided_rows: list[dict[str, object]] = []
    for row in manifest_rows:
        decided = dict(row)
        identifier = row.get("id")
        sha256 = row.get("sha256")
        approved = (
            isinstance(identifier, str)
            and isinstance(sha256, str)
            and _SHA256_RE.fullmatch(sha256) is not None
            and approvals.get(identifier) == sha256
            and row.get("exists") is True
        )
        decided["publish_allowed"] = approved
        decided["blocked_reason"] = (
            None
            if approved
            else "No matching checksum-bound OSF publication approval exists for this row."
        )
        decided_rows.append(decided)
    return decided_rows


def apply_registration_decision(
    freeze: dict[str, object], decision: dict[str, object] | None
) -> dict[str, object]:
    """Apply an accountable registration decision only to an exact current freeze."""
    decided = dict(freeze)
    reason = "registration_decision_missing"
    if decision and decision.get("status") == "approved_for_registration":
        expected = {
            "protocol_digest": decision.get("protocol_digest"),
            "analysis_manifest_digest": decision.get("analysis_manifest_digest"),
            "proposed_source_cutoff": decision.get("source_cutoff"),
        }
        mismatches = [field for field, value in expected.items() if decided.get(field) != value]
        if not mismatches:
            decided.update({
                "source_cutoff": decision["source_cutoff"],
                "source_cutoff_status": "approved",
                "review_approved": True,
                "review_record": "data/osf_review/registration_decision.json",
                "reviewer": decision.get("reviewer"),
                "reviewed_at": decision.get("reviewed_at"),
                "status": "approved_for_registration",
            })
            return decided
        reason = "registration_decision_drift:" + ",".join(mismatches)
    elif decision is not None:
        reason = "registration_decision_not_approved"
    decided["decision_reason"] = reason
    return decided


def build_registration_freeze(
    *, root: Path, sync_manifest_path: Path, source_cutoff: str = "not-frozen"
) -> dict[str, object]:
    """Build deterministic fingerprints for a future reviewed registration."""
    paths = sorted((*((root / "protocols").glob("*.md")), *((root / "reports").glob("*.md"))))
    proposed_cutoff = _latest_recorded_source_retrieval(root)
    return {
        "schema_version": "osf-registration-freeze-v1",
        "protocol_digest": _digest_paths(root, paths),
        "analysis_manifest_digest": _sha256_file(sync_manifest_path),
        "source_cutoff": source_cutoff,
        "proposed_source_cutoff": proposed_cutoff,
        "source_cutoff_status": "pending_accountable_approval",
        "source_cutoff_basis": (
            "Latest non-null retrieved_at in data/seed/source_snapshots.jsonl and "
            "data/seed/source_versions.jsonl; this proposal is not an approval."
        ),
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
    elif snapshot_errors := _validate_remote_snapshot(remote):
        reasons = ["invalid_remote_registration:" + ",".join(snapshot_errors)]
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
        "remote_snapshot_sha256": remote.get("snapshot_sha256") if remote else None,
        "network_io": False,
        "mutation_performed": False,
    }


def _validate_remote_snapshot(remote: dict[str, object]) -> list[str]:  # ruff:ignore[too-many-branches]
    """Validate the immutable metadata contract before comparing fingerprints."""
    errors: list[str] = []
    if remote.get("schema_version") != "osf-registration-snapshot-v1":
        errors.append("schema_version")
    registration_id = remote.get("registration_id")
    if not isinstance(registration_id, str) or not registration_id:
        errors.append("registration_id")
    registration_url = remote.get("registration_url")
    if not isinstance(registration_url, str) or not registration_url.startswith("https://osf.io/"):
        errors.append("registration_url")
    submitted_at = remote.get("submitted_at")
    if not isinstance(submitted_at, str) or not submitted_at:
        errors.append("submitted_at")
    if remote.get("immutable") is not True:
        errors.append("immutable")
    if remote.get("public") is not True:
        errors.append("public")
    if remote.get("pending_registration_approval") is not False:
        errors.append("pending_registration_approval")
    if remote.get("withdrawn") is not False:
        errors.append("withdrawn")
    if remote.get("embargoed") is not False:
        errors.append("embargoed")
    remote_verified_at = remote.get("remote_verified_at")
    if not isinstance(remote_verified_at, str) or not remote_verified_at:
        errors.append("remote_verified_at")
    receipt_sha256 = remote.get("receipt_sha256")
    if not isinstance(receipt_sha256, str) or _SHA256_RE.fullmatch(receipt_sha256) is None:
        errors.append("receipt_sha256")
    snapshot_sha256 = remote.get("snapshot_sha256")
    if not isinstance(snapshot_sha256, str) or _SHA256_RE.fullmatch(snapshot_sha256) is None:
        errors.append("snapshot_sha256")
    elif snapshot_sha256 != registration_snapshot_sha256(remote):
        errors.append("snapshot_sha256_mismatch")
    return errors


def registration_snapshot_sha256(snapshot: Mapping[str, object]) -> str:
    """Hash the canonical snapshot payload without its self-referential digest."""
    payload = {key: value for key, value in snapshot.items() if key != "snapshot_sha256"}
    canonical = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def build_remote_registration_snapshot(
    receipt: Mapping[str, object],
    freeze: Mapping[str, object],
) -> dict[str, object]:
    """Build a checksum-bound snapshot from a verified active OSF receipt."""
    if receipt.get("schema_version") != "osf-registration-receipt-v1":
        message = "invalid OSF registration receipt schema"
        raise ValueError(message)
    if receipt.get("status") != "registered":
        message = "OSF registration is not active"
        raise ValueError(message)
    if receipt.get("public") is not True or receipt.get("immutable") is not True:
        message = "OSF registration must be public and immutable"
        raise ValueError(message)
    if receipt.get("pending_registration_approval") is not False:
        message = "OSF registration approval is still pending"
        raise ValueError(message)
    if receipt.get("withdrawn") is True or receipt.get("embargoed") is True:
        message = "OSF registration must be active, unembargoed and not withdrawn"
        raise ValueError(message)
    registration_id = receipt.get("registration_id")
    registration_url = receipt.get("registration_url")
    submitted_at = receipt.get("registered_at")
    remote_verified_at = receipt.get("remote_verified_at")
    if not isinstance(registration_id, str) or not registration_id:
        message = "OSF registration receipt is missing registration_id"
        raise ValueError(message)
    if not isinstance(registration_url, str) or not registration_url.startswith("https://osf.io/"):
        message = "OSF registration receipt has an invalid registration_url"
        raise ValueError(message)
    if not isinstance(submitted_at, str) or not submitted_at:
        message = "OSF registration receipt is missing registered_at"
        raise ValueError(message)
    if not isinstance(remote_verified_at, str) or not remote_verified_at:
        message = "OSF registration receipt is missing remote_verified_at"
        raise ValueError(message)

    required = ("protocol_digest", "analysis_manifest_digest", "source_cutoff")
    missing = [field for field in required if not isinstance(freeze.get(field), str)]
    if missing or freeze.get("review_approved") is not True:
        detail = ",".join(missing) if missing else "review_approved"
        message = f"OSF registration freeze is incomplete: {detail}"
        raise ValueError(message)
    snapshot: dict[str, object] = {
        "schema_version": "osf-registration-snapshot-v1",
        "registration_id": registration_id,
        "registration_url": registration_url,
        "status": "registered",
        "submitted_at": submitted_at,
        "immutable": True,
        "public": True,
        "pending_registration_approval": False,
        "withdrawn": False,
        "embargoed": False,
        "remote_verified_at": remote_verified_at,
        "receipt_sha256": hashlib.sha256(
            json.dumps(
                dict(receipt),
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest(),
        "protocol_digest": freeze["protocol_digest"],
        "analysis_manifest_digest": freeze["analysis_manifest_digest"],
        "source_cutoff": freeze["source_cutoff"],
    }
    snapshot["snapshot_sha256"] = registration_snapshot_sha256(snapshot)
    return snapshot


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


def _latest_recorded_source_retrieval(root: Path) -> str | None:
    """Return the latest recorded source retrieval timestamp without network IO."""
    timestamps: list[str] = []
    for relative_path in ("data/seed/source_snapshots.jsonl", "data/seed/source_versions.jsonl"):
        path = root / relative_path
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            retrieved_at = row.get("retrieved_at")
            if isinstance(retrieved_at, str) and retrieved_at:
                timestamps.append(retrieved_at)
    return max(timestamps) if timestamps else None


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
    approved = (
        freeze.get("review_approved") is True and freeze.get("source_cutoff_status") == "approved"
    )
    checkbox = "x" if approved else " "
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
        "## OSF metadata contract",
        "",
        "- Title: `Reimbursement Atlas`",
        (
            "- Description: Comparative reimbursement-data research programme with explicit "
            "source, provenance, transformation and publication boundaries."
        ),
        (
            "- Contributors: **accountable contributor list must be confirmed in OSF before "
            "registration**"
        ),
        "- Code licence: `Apache-2.0`",
        (
            "- Underlying data terms: source-specific; preserve provider attribution and do not "
            "infer redistribution permission from the code licence."
        ),
        (
            "- Subjects: `health policy`, `health economics`, `reimbursement`, `data provenance`, "
            "`reproducible research`"
        ),
        (
            "- Tags: `reimbursement-atlas`, `health-policy`, `health-economics`, "
            "`data-provenance`, "
            "`reproducible-research`"
        ),
        (
            "- Required linked artefacts: protocol pack, research reports, data dictionary, "
            "publication manifest, Frictionless package, RO-Crate and transformation "
            "documentation."
        ),
        "",
        "## Temporal disclosure",
        "",
        (
            "Source discovery, acquisition engineering, fixture-based exploratory analyses and "
            "software implementation began before this registration."
        ),
        (
            "The powered 750-case mapping study, blinded reference review, threshold selection "
            "and one-time untouched holdout evaluation were completed before this registration."
        ),
        (
            "The registration must describe source acquisition, repository development, mapping "
            "adjudication and holdout evaluation as retrospective work. It must not describe "
            "those completed activities as preregistered or prospective."
        ),
        "",
        "## Required human decisions",
        "",
        f"- [{checkbox}] Methods review completed",
        f"- [{checkbox}] Domain/clinical review completed",
        f"- [{checkbox}] Source licence and derived-field review completed",
        f"- [{checkbox}] Governance and publication review completed",
        f"- [{checkbox}] Source cutoff and analysis manifest approved",
        "",
        "## Approval record",
        "",
        f"- Reviewer: `{freeze.get('reviewer', 'pending')}`",
        f"- Decision: `{'approved_for_registration' if approved else 'blocked'}`",
        f"- Reviewed at: `{freeze.get('reviewed_at', 'pending')}`",
        f"- Review record: `{freeze.get('review_record', 'pending')}`",
        "",
        (
            "Only exact checksum-bound rows authorized by the accountable publication decision "
            "may be synchronized."
        ),
        "Papers, preprints, raw source payloads and restricted descriptors remain excluded.",
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


def read_optional_object(path: Path) -> dict[str, object] | None:
    """Read an optional JSON decision document."""
    if not path.is_file():
        return None
    return _read_object(path)

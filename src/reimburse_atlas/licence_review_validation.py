"""Validate checksum-bound human licence decisions without granting approval."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

REQUIRED_DECISION_FIELDS = {
    "review_id",
    "relative_path",
    "checksum_sha256",
    "decision",
    "reviewer",
    "reviewed_at",
    "source_terms",
    "attribution",
    "redistribution_permission",
    "restrictions",
    "evidence",
}
VALID_DECISIONS = {"approved", "blocked"}


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Read object rows from JSONL and return parse errors without raising."""
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    if not path.exists():
        return rows, []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return rows, [f"could not read {path}: {exc}"]
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path}:{line_number}: row must be a JSON object")
            continue
        rows.append(cast("dict[str, Any]", value))
    return rows, errors


def _validate_queue_row(
    row: dict[str, Any],
    *,
    index: int,
    queue_path: Path,
    root: Path,
    queue_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    """Validate one generated queue row and index it by review identifier."""
    errors: list[str] = []
    review_id = row.get("review_id")
    relative_path = row.get("relative_path")
    checksum = row.get("checksum_sha256")
    status = row.get("review_status")
    if not isinstance(review_id, str) or not review_id:
        return [f"{queue_path}:{index}: review_id is required"]
    if review_id in queue_by_id:
        errors.append(f"{queue_path}:{index}: duplicate review_id {review_id}")
    queue_by_id[review_id] = row
    if not isinstance(relative_path, str) or not relative_path:
        errors.append(f"{queue_path}:{index}: relative_path is required")
    else:
        candidate = (root / relative_path).resolve()
        if root.resolve() not in candidate.parents:
            errors.append(f"{queue_path}:{index}: path escapes repository: {relative_path}")
        elif not candidate.is_file():
            errors.append(f"{queue_path}:{index}: candidate file missing: {relative_path}")
        elif isinstance(checksum, str):
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if digest != checksum:
                errors.append(f"{queue_path}:{index}: checksum mismatch: {relative_path}")
        else:
            errors.append(f"{queue_path}:{index}: checksum_sha256 is required")
    if status not in {"pending", "approved", "blocked"}:
        errors.append(f"{queue_path}:{index}: invalid review_status {status!r}")
    if status == "pending" and any(row.get(field) for field in ("reviewer", "reviewed_at")):
        errors.append(f"{queue_path}:{index}: pending rows cannot contain reviewer metadata")
    return errors


def _validate_decision_row(
    decision: dict[str, Any],
    *,
    index: int,
    decisions_path: Path,
    queue_by_id: dict[str, dict[str, Any]],
    seen_decisions: set[str],
) -> list[str]:
    """Validate one human decision against the generated queue index."""
    errors: list[str] = []
    missing = sorted(REQUIRED_DECISION_FIELDS - set(decision))
    if missing:
        return [f"{decisions_path}:{index}: missing fields: {', '.join(missing)}"]
    review_id = decision["review_id"]
    if not isinstance(review_id, str) or review_id in seen_decisions:
        errors.append(f"{decisions_path}:{index}: duplicate or invalid review_id")
    seen_decisions.add(str(review_id))
    queue_row = queue_by_id.get(str(review_id))
    if queue_row is None:
        errors.append(f"{decisions_path}:{index}: unknown review_id {review_id}")
        return errors
    if decision["relative_path"] != queue_row.get("relative_path"):
        errors.append(f"{decisions_path}:{index}: relative_path does not match queue")
    if decision["checksum_sha256"] != queue_row.get("checksum_sha256"):
        errors.append(f"{decisions_path}:{index}: checksum does not match queue")
    if decision["decision"] not in VALID_DECISIONS:
        errors.append(f"{decisions_path}:{index}: decision must be approved or blocked")
    for field in REQUIRED_DECISION_FIELDS - {
        "review_id",
        "relative_path",
        "checksum_sha256",
        "decision",
    }:
        if not isinstance(decision[field], str) or not decision[field].strip():
            errors.append(f"{decisions_path}:{index}: {field} must be non-empty")
    return errors


def validate_licence_review_queue(
    queue_path: Path,
    *,
    root: Path,
    decisions_path: Path | None = None,
) -> list[str]:
    """Return fail-closed validation errors for queue and optional decisions."""
    queue_rows, errors = _read_jsonl(queue_path)
    queue_by_id: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(queue_rows, start=1):
        errors.extend(
            _validate_queue_row(
                row,
                index=index,
                queue_path=queue_path,
                root=root,
                queue_by_id=queue_by_id,
            )
        )

    if decisions_path is None:
        return errors
    decision_rows, decision_errors = _read_jsonl(decisions_path)
    errors.extend(decision_errors)
    seen_decisions: set[str] = set()
    for index, decision in enumerate(decision_rows, start=1):
        errors.extend(
            _validate_decision_row(
                decision,
                index=index,
                decisions_path=decisions_path,
                queue_by_id=queue_by_id,
                seen_decisions=seen_decisions,
            )
        )
    return errors

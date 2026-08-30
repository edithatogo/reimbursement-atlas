"""Owner-delegated renewal of bounded operational metadata, never source rights."""

from __future__ import annotations

import csv
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

POLICY_PATH = Path("data/licence_review/standing_scope.json")


def _object(value: object) -> dict[str, Any]:
    return cast("dict[str, Any]", value) if isinstance(value, dict) else {}


def standing_policy(root: Path) -> dict[str, Any]:
    """Read an explicit policy; absent or malformed configuration grants nothing."""
    try:
        value = _object(json.loads((root / POLICY_PATH).read_text(encoding="utf-8")))
    except OSError, ValueError:
        return {}
    if value.get("schema_version") != "standing-approval-v1":
        return {}
    return value


def _rows(raw: str, suffix: str) -> list[Any]:
    if suffix == ".csv":
        return list(csv.DictReader(raw.splitlines()))
    if suffix == ".jsonl":
        return [json.loads(line) for line in raw.splitlines() if line.strip()]
    return [json.loads(raw)] if suffix == ".json" else []


def _safe_shape(row: dict[str, Any]) -> bool:
    """Receipts contain scalar metadata, scalar lists or numeric status counters."""
    for key, value in row.items():
        if isinstance(value, dict):
            if key != "status_counts" or not all(
                type(item) is int and item >= 0 for item in cast("dict[str, Any]", value).values()
            ):
                return False
        elif isinstance(value, list):
            if not all(
                isinstance(item, (str, int, float, bool, type(None)))
                for item in cast("list[Any]", value)
            ):
                return False
        elif not isinstance(value, (str, int, float, bool, type(None))):
            return False
    return True


def _valid_risk_values(values: dict[str, Any]) -> bool:
    return bool(values) and all(
        isinstance(allowed, list)
        and bool(cast("list[Any]", allowed))
        and all(isinstance(item, str) for item in cast("list[Any]", allowed))
        for allowed in values.values()
    )


@lru_cache(maxsize=64)
def _content_valid(raw: str, suffix: str, scope_json: str) -> bool:
    """Cache only exact content/contract bytes, never timestamps or path identities."""
    try:
        rows = _rows(raw, suffix)
        scope = _object(json.loads(scope_json))
    except ValueError, csv.Error:
        return False
    fields = scope.get("fields", [])
    risk_values = _object(scope.get("risk_values"))
    if not rows or not isinstance(fields, list) or not _valid_risk_values(risk_values):
        return False
    return all(
        bool(_object(row))
        and _safe_shape(_object(row))
        and set(_object(row)) == set(cast("list[str]", fields))
        and all(
            json.dumps(_object(row).get(key), sort_keys=True) in allowed
            for key, allowed in risk_values.items()
        )
        for row in rows
    )


def metadata_scope_valid(root: Path, relative_path: str) -> bool:
    """Allow checksum churn only for enumerated fields, source families and rights."""
    policy = standing_policy(root)
    scope = _object(_object(policy.get("metadata")).get(relative_path))
    rights = _object(policy.get("rights_files"))
    path = root / relative_path
    if not scope or not rights or path.is_symlink():
        return False
    if not path.resolve().is_relative_to(root.resolve()):
        return False
    try:
        rights_valid = all(
            hashlib.sha256((root / name).read_bytes()).hexdigest() == checksum
            for name, checksum in rights.items()
        )
        return rights_valid and _content_valid(
            path.read_text(encoding="utf-8"), path.suffix, json.dumps(scope, sort_keys=True)
        )
    except OSError, ValueError:
        return False

"""Reconcile historical locators with existing checksum-bound acquisitions."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, cast

IDENTITIES = {
    "20260701_MBSONLINE_IMAP.TXT": "au_mbs_20260701_imap_txt",
    "20260701_MBSONLINE_DESC.TXT": "au_mbs_20260701_desc_txt",
}


def _rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    values = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not all(isinstance(value, dict) for value in values):
        message = "Expected JSONL object rows"
        raise ValueError(message)
    return cast("list[dict[str, Any]]", values)


def _has_checksum(row: dict[str, Any]) -> bool:
    digest, size = row.get("checksum_sha256"), row.get("byte_size")
    return (
        isinstance(digest, str)
        and re.fullmatch(r"[0-9a-f]{64}", digest) is not None
        and type(size) is int
        and size > 0
    )


def _reviewed_match(root: Path, target: dict[str, Any]) -> dict[str, Any] | None:
    source_file_id = IDENTITIES.get(str(target.get("file_name")))
    files = [
        r for r in _rows(root / "data/seed/source_files.jsonl") if r.get("id") == source_file_id
    ]
    if (
        source_file_id is None
        or len(files) != 1
        or files[0].get("source_id") != target.get("source_id")
        or files[0].get("file_name") != target.get("file_name")
    ):
        return None
    file = files[0]
    validations = [
        r
        for r in _rows(root / "data/derived/source_validation/source_content_validation.jsonl")
        if r.get("source_file_id") == source_file_id
        and r.get("source_id") == file.get("source_id")
        and r.get("source_version_id") == file.get("source_version_id")
        and r.get("validation_status") == "pass"
        and _has_checksum(r)
    ]
    if len(validations) != 1:
        return None
    validation = validations[0]
    ref = str(validation.get("local_target_ref", ""))
    if not ref.startswith("reviewed_bundle:"):
        return None
    bundle = (root / ref.removeprefix("reviewed_bundle:")).resolve()
    if not bundle.is_relative_to((root / "data/derived/reviewed_source_bundles").resolve()):
        return None
    path = bundle / "source_snapshots.jsonl"
    matches = [
        r
        for r in _rows(path)
        if all(
            r.get(k) == validation.get(k)
            for k in ("source_id", "source_version_id", "checksum_sha256", "byte_size")
        )
    ]
    if len(matches) != 1:
        return None
    return {
        "target_id": target["id"],
        "source_file_id": source_file_id,
        "snapshot_id": matches[0]["id"],
        "source_version_id": file["source_version_id"],
        "checksum_sha256": validation["checksum_sha256"],
        "byte_size": validation["byte_size"],
        "snapshot_manifest": path.relative_to(root.resolve()).as_posix(),
        "snapshot_manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "status": "acquisition_previously_evidenced",
        "current_raw_availability": "not_asserted",
    }


def build_reconciliation(root: Path, targets: list[dict[str, Any]]) -> dict[str, Any]:
    """Count evidenced target identities without converting HTTP failures to transfers."""
    ids = [row["id"] for row in targets]
    if len(set(ids)) != len(ids):
        message = "Duplicate historical target identities"
        raise ValueError(message)
    by_id = {row["id"]: row for row in targets}
    downloaded = {
        row["id"]
        for row in _rows(root / "data/derived/historical_sources/historical_source_downloads.jsonl")
        if row.get("status") in {"downloaded", "cached"} and _has_checksum(row)
        if row.get("id") in by_id
        and row.get("source_id") == by_id[row["id"]].get("source_id")
        and row.get("file_name") == by_id[row["id"]].get("file_name")
        and row.get("source_url") == by_id[row["id"]].get("file_url")
        and isinstance(row.get("source_url"), str)
        and bool(row["source_url"])
    }
    aliases = [
        match
        for target in targets
        if target["id"] not in downloaded
        if (match := _reviewed_match(root, target)) is not None
    ]
    evidenced = downloaded | {row["target_id"] for row in aliases}
    return {
        "schema_version": "historical-source-identity-reconciliation-v1",
        "target_count": len(ids),
        "direct_download_receipt_count": len(downloaded),
        "reviewed_snapshot_alias_count": len(aliases),
        "acquisition_evidenced_target_count": len(evidenced),
        "unresolved_target_ids": sorted(set(ids) - evidenced),
        "reconciled_targets": aliases,
        "current_raw_availability": "not_asserted",
        "publication_effect": "none",
        "locator_failures_preserved": True,
    }

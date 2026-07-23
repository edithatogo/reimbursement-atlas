"""Validate and combine isolated mapping reviews into the canonical ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.io import write_jsonl
from reimburse_atlas.registry import project_root

MANIFEST = Path("data/derived/mapping_study/blind_review_packets/manifest.json")
ROLE_FILES = {
    "reviewer_a": Path("data/mapping_study/reviewer_a_reviews.jsonl"),
    "reviewer_b": Path("data/mapping_study/reviewer_b_reviews.jsonl"),
}
OUTPUT = Path("data/mapping_study/blind_reviews.jsonl")
SUMMARY = Path("data/derived/mapping_study/blind_review_summary.json")


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        cast("dict[str, Any]", json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_ledger(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return a canonical ledger only when both isolated role files are complete."""
    manifest = cast(
        "dict[str, Any]",
        json.loads((root / MANIFEST).read_text(encoding="utf-8")),
    )
    frame_sha256 = str(manifest["candidate_frame_sha256"])
    expected_count = int(manifest["case_count"])
    by_role: dict[str, dict[str, dict[str, Any]]] = {}
    role_hashes: dict[str, str] = {}
    for role, relative_path in ROLE_FILES.items():
        path = root / relative_path
        rows = _jsonl(path)
        indexed = {str(row.get("case_id")): row for row in rows}
        if len(rows) != expected_count or len(indexed) != expected_count:
            message = f"{role} review must contain {expected_count} unique cases"
            raise ValueError(message)
        if any(
            row.get("reviewer_role") != role or row.get("candidate_frame_sha256") != frame_sha256
            for row in rows
        ):
            message = f"{role} review metadata does not match the frozen frame"
            raise ValueError(message)
        by_role[role] = indexed
        role_hashes[role] = hashlib.sha256(path.read_bytes()).hexdigest()
    if set(by_role["reviewer_a"]) != set(by_role["reviewer_b"]):
        message = "isolated reviewers did not assess the same case set"
        raise ValueError(message)
    ledger = sorted(
        [*by_role["reviewer_a"].values(), *by_role["reviewer_b"].values()],
        key=lambda row: (str(row["case_id"]), str(row["reviewer_role"])),
    )
    agreements = sum(
        by_role["reviewer_a"][case_id]["decision"] == by_role["reviewer_b"][case_id]["decision"]
        for case_id in by_role["reviewer_a"]
    )
    summary = {
        "schema_version": "mapping-blind-review-summary-v1",
        "candidate_frame_sha256": frame_sha256,
        "reviewer_case_count": expected_count,
        "ledger_record_count": len(ledger),
        "role_file_sha256": role_hashes,
        "agreement_count": agreements,
        "disagreement_count": expected_count - agreements,
        "percent_agreement": agreements / expected_count,
        "independent_roles_complete": True,
        "accountable_adjudication_complete": False,
    }
    return ledger, summary


def main() -> None:
    """Write the canonical review ledger and bounded agreement summary."""
    root = project_root()
    ledger, summary = build_ledger(root)
    write_jsonl(ledger, root / OUTPUT)
    summary_path = root / SUMMARY
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

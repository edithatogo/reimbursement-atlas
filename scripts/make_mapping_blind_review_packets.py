"""Generate role-isolated mapping review packets from a frozen candidate frame."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.io import write_jsonl
from reimburse_atlas.registry import project_root

FRAME = Path("data/derived/mapping_study/candidate_frame.jsonl")
OUTPUT = Path("data/derived/mapping_study/blind_review_packets")


def _jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [
        cast("dict[str, Any]", json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_packets(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return blinded cases and a frozen-frame manifest."""
    frame_path = root / FRAME
    if not frame_path.is_file():
        return [], {"status": "blocked_missing_frame", "case_count": 0}
    frame_sha256 = hashlib.sha256(frame_path.read_bytes()).hexdigest()
    lookup: dict[tuple[str, str, str], dict[str, Any]] = {}
    for path in sorted(
        (root / "data/derived/reviewed_source_bundles").glob("**/*schedule_items.jsonl")
    ):
        for row in _jsonl(path):
            provenance = cast("dict[str, Any]", row.get("provenance", {}))
            key = (
                str(row.get("source_id", "")),
                str(row.get("item_code", "")),
                str(provenance.get("source_version", "")),
            )
            lookup[key] = row
    cases: list[dict[str, Any]] = []
    missing_evidence: list[str] = []
    for candidate in _jsonl(frame_path):
        versions = cast("list[str]", candidate["source_versions"])
        left = lookup.get((
            str(candidate["left_source_id"]),
            str(candidate["left_code"]),
            versions[0],
        ))
        right = lookup.get((
            str(candidate["right_source_id"]),
            str(candidate["right_code"]),
            versions[1],
        ))
        if left is None or right is None:
            missing_evidence.append(str(candidate["case_id"]))
            continue
        cases.append({
            "schema_version": "mapping-blind-review-case-v1",
            "candidate_frame_sha256": frame_sha256,
            "case_id": candidate["case_id"],
            "family": candidate["family"],
            "left": _evidence(left, versions[0], candidate["provenance_checksums"][0]),
            "right": _evidence(right, versions[1], candidate["provenance_checksums"][1]),
            "allowed_decisions": ["positive", "negative", "exclude", "uncertain"],
        })
    cases.sort(key=lambda row: str(row["case_id"]))
    return cases, {
        "schema_version": "mapping-blind-review-packet-manifest-v1",
        "status": "ready" if len(cases) == 1500 and not missing_evidence else "blocked",
        "candidate_frame_sha256": frame_sha256,
        "case_count": len(cases),
        "missing_evidence_case_ids": missing_evidence,
        "hypotheses_exposed": False,
        "split_assignment_exposed": False,
        "reviewer_roles": ["reviewer_a", "reviewer_b"],
    }


def _evidence(row: dict[str, Any], version: str, checksum: object) -> dict[str, Any]:
    provenance = cast("dict[str, Any]", row.get("provenance", {}))
    return {
        "source_id": row["source_id"],
        "code": row["item_code"],
        "label": row["item_label"],
        "description": row.get("item_description"),
        "domain": row["domain"],
        "source_version": version,
        "bundle_sha256": checksum,
        "source_url": provenance.get("source_url"),
    }


def write_packets(root: Path, cases: list[dict[str, Any]], manifest: dict[str, Any]) -> None:
    """Write identical role packets and checksum parity evidence."""
    output = root / OUTPUT
    output.mkdir(parents=True, exist_ok=True)
    role_hashes: dict[str, str] = {}
    for role in ("reviewer_a", "reviewer_b"):
        path = write_jsonl(cases, output / f"{role}_cases.jsonl")
        role_hashes[role] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest["role_packet_sha256"] = role_hashes
    manifest["role_packets_identical"] = len(set(role_hashes.values())) == 1
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    """Generate the blinded review packets."""
    root = project_root()
    cases, manifest = build_packets(root)
    write_packets(root, cases, manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

"""Validate adjudication proposals and build one checksum-bound owner packet."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root

FRAME = Path("data/derived/mapping_study/candidate_frame.jsonl")
REVIEWS = Path("data/mapping_study/blind_reviews.jsonl")
PROPOSALS = Path("data/mapping_study/adjudication_proposals.jsonl")
OUTPUT = Path("data/derived/mapping_study/adjudication_owner_packet.json")
FAMILY_LABEL_TARGETS = {
    "procedures_pathology": 150,
    "medicines": 100,
    "genomics_coverage": 75,
    "devices_other": 50,
}


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        cast("dict[str, Any]", json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_packet(root: Path) -> dict[str, Any]:
    """Return a bounded owner packet after validating every proposal."""
    frame_path = root / FRAME
    proposal_path = root / PROPOSALS
    frame_sha256 = hashlib.sha256(frame_path.read_bytes()).hexdigest()
    frame = {str(row["case_id"]): row for row in _jsonl(frame_path)}
    proposals = {str(row["case_id"]): row for row in _jsonl(proposal_path)}
    if set(proposals) != set(frame):
        message = "adjudication proposals must cover the complete frozen frame"
        raise ValueError(message)
    reviews: dict[str, dict[str, str]] = {}
    for row in _jsonl(root / REVIEWS):
        reviews.setdefault(str(row["case_id"]), {})[str(row["reviewer_role"])] = str(
            row["decision"]
        )
    for case_id, proposal in proposals.items():
        if proposal.get("candidate_frame_sha256") != frame_sha256:
            message = f"proposal frame checksum mismatch: {case_id}"
            raise ValueError(message)
        pair = reviews.get(case_id, {})
        if proposal.get("reviewer_a_decision") != pair.get("reviewer_a") or proposal.get(
            "reviewer_b_decision"
        ) != pair.get("reviewer_b"):
            message = f"proposal reviewer decisions do not match blind ledger: {case_id}"
            raise ValueError(message)
    counts = Counter(
        (str(frame[case_id]["family"]), str(proposal["final_decision"]))
        for case_id, proposal in proposals.items()
    )
    family_counts = {
        family: {label: counts[family, label] for label in ("positive", "negative", "exclude")}
        for family in FAMILY_LABEL_TARGETS
    }
    quota_gaps = {
        family: {
            label: max(0, target - counts[family, label]) for label in ("positive", "negative")
        }
        for family, target in FAMILY_LABEL_TARGETS.items()
    }
    total_gap = sum(gap for family in quota_gaps.values() for gap in family.values())
    proposal_sha256 = hashlib.sha256(proposal_path.read_bytes()).hexdigest()
    return {
        "schema_version": "mapping-adjudication-owner-packet-v1",
        "status": "ready_for_owner_approval" if total_gap == 0 else "blocked_candidate_spectrum",
        "candidate_frame_sha256": frame_sha256,
        "proposal_sha256": proposal_sha256,
        "proposal_count": len(proposals),
        "family_decision_counts": family_counts,
        "family_label_quota_gaps": quota_gaps,
        "total_quota_gap": total_gap,
        "accountable_owner_approval_required": True,
        "approval_effect": (
            "Approval freezes only the proposed reference decisions for this exact frame and "
            "proposal checksum; it does not waive family quotas or authorize evidence claims."
        ),
    }


def main() -> None:
    """Write the current checksum-bound owner packet."""
    root = project_root()
    packet = build_packet(root)
    output = root / OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(packet, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

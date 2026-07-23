"""Validate and combine isolated mapping reviews into the canonical ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.io import write_jsonl
from reimburse_atlas.mapping_study_paths import DEFAULT_CYCLE, mapping_study_paths
from reimburse_atlas.registry import project_root


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        cast("dict[str, Any]", json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _review_receipts(
    root: Path,
    *,
    review_root: Path,
    manifest: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Validate session separation for receipt-enabled packet manifests."""
    if manifest.get("schema_version") != "mapping-blind-review-packet-manifest-v2":
        return {}
    receipts: dict[str, dict[str, Any]] = {}
    review_packet_sha256 = str(
        manifest.get("private_packet_sha256")
        or cast("dict[str, str]", manifest["role_packet_sha256"])["reviewer_a"]
    )
    for role in ("reviewer_a", "reviewer_b"):
        path = root / review_root / f"{role}_receipt.json"
        if not path.is_file():
            message = f"{role} independent-review receipt is required"
            raise ValueError(message)
        receipt = cast("dict[str, Any]", json.loads(path.read_text(encoding="utf-8")))
        required_attestations = {
            "other_review_not_accessed": True,
            "hypotheses_not_accessed": True,
            "split_assignment_not_accessed": True,
        }
        expected = {
            "schema_version": "mapping-reviewer-session-receipt-v1",
            "reviewer_role": role,
            "candidate_frame_sha256": manifest["candidate_frame_sha256"],
            "packet_sha256": review_packet_sha256,
            "isolation_attestation": required_attestations,
        }
        text_fields = ("reviewer_session_id", "bounded_mandate", "started_at", "completed_at")
        if any(receipt.get(key) != value for key, value in expected.items()) or any(
            not str(receipt.get(field, "")).strip() for field in text_fields
        ):
            message = f"{role} independent-review receipt is invalid"
            raise ValueError(message)
        receipts[role] = receipt
    if (
        receipts["reviewer_a"]["reviewer_session_id"]
        == receipts["reviewer_b"]["reviewer_session_id"]
    ):
        message = "isolated reviewers must use distinct session identifiers"
        raise ValueError(message)
    return receipts


def build_ledger(  # ruff:ignore[too-many-locals]
    root: Path, cycle: str = DEFAULT_CYCLE
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return a canonical ledger only when both isolated role files are complete."""
    paths = mapping_study_paths(cycle)
    manifest = cast(
        "dict[str, Any]",
        json.loads((root / paths.manifest).read_text(encoding="utf-8")),
    )
    frame_sha256 = str(manifest["candidate_frame_sha256"])
    expected_count = int(manifest["case_count"])
    receipts = _review_receipts(root, review_root=paths.review, manifest=manifest)
    packet_path = root / paths.packets / "reviewer_a_cases.jsonl"
    packet_cases = (
        {str(row["case_id"]): row for row in _jsonl(packet_path)} if packet_path.is_file() else {}
    )
    by_role: dict[str, dict[str, dict[str, Any]]] = {}
    role_hashes: dict[str, str] = {}
    role_files = {"reviewer_a": paths.reviewer_a, "reviewer_b": paths.reviewer_b}
    for role, relative_path in role_files.items():
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
        if any(
            packet_cases.get(case_id, {}).get("target_relation") != row.get("target_relation")
            for case_id, row in indexed.items()
            if packet_cases.get(case_id, {}).get("schema_version") == "mapping-blind-review-case-v2"
        ):
            message = f"{role} review target relation does not match the blinded case"
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
    decisions = ("positive", "negative", "exclude", "uncertain")
    pair_counts = Counter(
        (
            str(by_role["reviewer_a"][case_id]["decision"]),
            str(by_role["reviewer_b"][case_id]["decision"]),
        )
        for case_id in by_role["reviewer_a"]
    )
    marginal_a = Counter(str(row["decision"]) for row in by_role["reviewer_a"].values())
    marginal_b = Counter(str(row["decision"]) for row in by_role["reviewer_b"].values())
    expected_agreement = sum(
        marginal_a[decision] * marginal_b[decision] for decision in decisions
    ) / (expected_count * expected_count)
    observed_agreement = agreements / expected_count
    kappa = (
        (observed_agreement - expected_agreement) / (1 - expected_agreement)
        if expected_agreement < 1
        else 1.0
    )
    family_summary: dict[str, dict[str, int | float]] = {}
    for family in sorted({str(row.get("family")) for row in packet_cases.values()}):
        case_ids = [
            case_id for case_id, row in packet_cases.items() if str(row.get("family")) == family
        ]
        family_agreements = sum(
            by_role["reviewer_a"][case_id]["decision"] == by_role["reviewer_b"][case_id]["decision"]
            for case_id in case_ids
        )
        family_summary[family] = {
            "case_count": len(case_ids),
            "agreement_count": family_agreements,
            "disagreement_count": len(case_ids) - family_agreements,
            "percent_agreement": family_agreements / len(case_ids),
        }
    summary = {
        "schema_version": "mapping-blind-review-summary-v1",
        "study_cycle": cycle,
        "candidate_frame_sha256": frame_sha256,
        "reviewer_case_count": expected_count,
        "ledger_record_count": len(ledger),
        "role_file_sha256": role_hashes,
        "review_receipt_sha256": {
            role: hashlib.sha256(
                (root / paths.review / f"{role}_receipt.json").read_bytes()
            ).hexdigest()
            for role in receipts
        },
        "agreement_count": agreements,
        "disagreement_count": expected_count - agreements,
        "percent_agreement": agreements / expected_count,
        "cohen_kappa": kappa,
        "decision_pair_counts": {
            f"{left}->{right}": pair_counts[left, right]
            for left in decisions
            for right in decisions
        },
        "family_agreement": family_summary,
        "independent_roles_complete": True,
        "independence_receipts_validated": bool(receipts),
        "accountable_adjudication_complete": False,
    }
    return ledger, summary


def main() -> None:
    """Write the canonical review ledger and bounded agreement summary."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle", default=DEFAULT_CYCLE)
    args = parser.parse_args()
    root = project_root()
    paths = mapping_study_paths(args.cycle)
    ledger, summary = build_ledger(root, args.cycle)
    write_jsonl(ledger, root / paths.blind_reviews)
    summary_path = root / paths.blind_review_summary
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

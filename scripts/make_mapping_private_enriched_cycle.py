"""Freeze a mapping cycle with local-only CPT evidence and public redacted packets."""

from __future__ import annotations

import argparse
import hashlib
import json
import operator
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.crosswalk import tokenise
from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.registry import project_root

CPT_POSITIVE_TARGET = 400
PROCEDURE_NEGATIVE_TARGET = 200
OUTPUT_CYCLE = "expansion_v9"


def build_enriched_cycle(
    *,
    base_frame: list[dict[str, Any]],
    local_cpt_candidates: list[dict[str, Any]],
    mbs_bundle_sha256: str,
    cpt_archive_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, object]]:
    """Return public frame, private evidence cases and summary."""
    cpt_rows = _select_cpt_rows(
        local_cpt_candidates,
        mbs_bundle_sha256=mbs_bundle_sha256,
        cpt_archive_sha256=cpt_archive_sha256,
    )
    procedure_negatives = [
        row
        for row in base_frame
        if row["family"] == "procedures_pathology"
        and row["proposed_label_hypothesis"] == "negative_candidate"
    ][:PROCEDURE_NEGATIVE_TARGET]
    retained = [row for row in base_frame if row["family"] != "procedures_pathology"]
    frame = sorted(
        [*cpt_rows, *procedure_negatives, *retained],
        key=operator.itemgetter("case_id"),
    )
    if len(frame) != 1500:
        message = f"enriched cycle must contain 1,500 rows, observed {len(frame)}"
        raise ValueError(message)
    family_counts: dict[str, int] = {}
    for row in frame:
        family = str(row["family"])
        family_counts[family] = family_counts.get(family, 0) + 1
    expected = {
        "procedures_pathology": 600,
        "medicines": 400,
        "genomics_coverage": 300,
        "devices_other": 200,
    }
    if family_counts != expected:
        message = f"family quota mismatch: {family_counts}"
        raise ValueError(message)
    private_lookup = {str(row["candidate_id"]): row for row in local_cpt_candidates}
    private_cases = [
        _private_case(row, private_lookup)
        for row in frame
        if row["right_source_id"] == "us_cms_pfs_local_cpt"
    ]
    summary: dict[str, object] = {
        "schema_version": "mapping-candidate-frame-summary-v3",
        "study_cycle": OUTPUT_CYCLE,
        "status": "ready_for_private_blinded_review",
        "candidate_count": len(frame),
        "effective_unique_groups": len({row["duplicate_group"] for row in frame}),
        "family_summary": {
            family: {
                "target": target,
                "available": family_counts[family],
                "gap": 0,
                "status": "ready",
            }
            for family, target in expected.items()
        },
        "private_cpt_case_count": len(private_cases),
        "fixture_rows_used": 0,
        "review_blinded": True,
        "split_assigned": False,
        "descriptor_storage": "ignored_local_only",
    }
    return frame, private_cases, summary


def _select_cpt_rows(
    candidates: list[dict[str, Any]],
    *,
    mbs_bundle_sha256: str,
    cpt_archive_sha256: str,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    used_left: set[str] = set()
    used_right: set[str] = set()
    used_groups: set[str] = set()
    ranked = sorted(
        candidates,
        key=lambda row: (-float(row["token_jaccard"]), str(row["candidate_id"])),
    )
    for row in ranked:
        left_code = str(row["left_code"])
        right_code = str(row["right_code"])
        duplicate_group = hashlib.sha256(
            "|".join(
                sorted((
                    " ".join(sorted(tokenise(str(row["left_description"])))),
                    " ".join(sorted(tokenise(str(row["right_description"])))),
                ))
            ).encode()
        ).hexdigest()[:16]
        if left_code in used_left or right_code in used_right or duplicate_group in used_groups:
            continue
        identity = f"procedures_pathology|au_mbs|{left_code}|us_cms_pfs_local_cpt|{right_code}"
        selected.append({
            "schema_version": "mapping-candidate-frame-v2",
            "case_id": f"map_{hashlib.sha256(identity.encode()).hexdigest()[:20]}",
            "family": "procedures_pathology",
            "target_relation": "clinically_comparable_service_or_test_class",
            "left_source_id": "au_mbs",
            "left_code": left_code,
            "right_source_id": "us_cms_pfs_local_cpt",
            "right_code": right_code,
            "source_versions": ["au_mbs_20260701_txt_pair", "us_cms_pfs_rvu26c"],
            "provenance_checksums": [mbs_bundle_sha256, cpt_archive_sha256],
            "evidence_fields": ["item_code", "local_restricted_descriptor"],
            "proposed_label_hypothesis": "positive_candidate",
            "candidate_score": row["token_jaccard"],
            "proposed_difficulty": (
                "routine" if float(row["token_jaccard"]) >= 0.5 else "ambiguous"
            ),
            "duplicate_group": duplicate_group,
            "private_candidate_id": row["candidate_id"],
        })
        used_left.add(left_code)
        used_right.add(right_code)
        used_groups.add(duplicate_group)
        if len(selected) == CPT_POSITIVE_TARGET:
            break
    if len(selected) != CPT_POSITIVE_TARGET:
        message = f"insufficient unique local CPT hypotheses: {len(selected)}"
        raise ValueError(message)
    return selected


def _private_case(
    frame_row: dict[str, Any],
    private_lookup: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    evidence = private_lookup[str(frame_row["private_candidate_id"])]
    return {
        "schema_version": "mapping-private-blind-review-case-v1",
        "case_id": frame_row["case_id"],
        "family": frame_row["family"],
        "target_relation": frame_row["target_relation"],
        "decision_question": (
            "Do the two records support a clinically comparable service or test class? "
            "Do not infer billing-code equivalence, identical coverage, or equal price."
        ),
        "left": {
            "source_id": "au_mbs",
            "code": evidence["left_code"],
            "description": evidence["left_description"],
        },
        "right": {
            "source_id": "us_cms_pfs_local_cpt",
            "code": evidence["right_code"],
            "description": evidence["right_description"],
        },
        "allowed_decisions": ["positive", "negative", "exclude", "uncertain"],
    }


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        cast("dict[str, Any]", json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def expand_private_cases(
    root: Path,
    frame: list[dict[str, Any]],
    cpt_cases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Join public-bundle evidence to the restricted CPT cases for local review."""
    by_case = {str(row["case_id"]): row for row in cpt_cases}
    lookup: dict[tuple[str, str, str], dict[str, Any]] = {}
    bundle_root = root / "data/derived/reviewed_source_bundles"
    for path in sorted(bundle_root.glob("**/*schedule_items.jsonl")):
        for row in _jsonl(path):
            provenance = cast("dict[str, Any]", row.get("provenance", {}))
            lookup[
                str(row.get("source_id", "")),
                str(row.get("item_code", "")),
                str(provenance.get("source_version", "")),
            ] = row
    for candidate in frame:
        case_id = str(candidate["case_id"])
        if case_id in by_case:
            continue
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
            message = f"missing public evidence for {case_id}"
            raise ValueError(message)
        by_case[case_id] = {
            "schema_version": "mapping-private-blind-review-case-v1",
            "case_id": case_id,
            "family": candidate["family"],
            "target_relation": candidate["target_relation"],
            "decision_question": (
                "Do the records satisfy the stated target relation? Positive does not imply "
                "billing-code equivalence, identical coverage, or equal price."
            ),
            "left": _public_evidence(left),
            "right": _public_evidence(right),
            "allowed_decisions": ["positive", "negative", "exclude", "uncertain"],
        }
    return [by_case[case_id] for case_id in sorted(by_case)]


def _public_evidence(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": row["source_id"],
        "code": row["item_code"],
        "label": row["item_label"],
        "description": row.get("item_description"),
        "domain": row["domain"],
    }


def write_enriched_cycle(
    root: Path,
    frame: list[dict[str, Any]],
    private_cases: list[dict[str, Any]],
    summary: dict[str, object],
) -> None:
    """Write tracked redacted evidence and ignored private packets."""
    derived = root / "data/derived/mapping_study" / OUTPUT_CYCLE
    private = root / "data/local/mapping_study" / OUTPUT_CYCLE
    packets = derived / "blind_review_packets"
    derived.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)
    packets.mkdir(parents=True, exist_ok=True)
    frame_path = write_jsonl(frame, derived / "candidate_frame.jsonl")
    write_csv(frame, derived / "candidate_frame.csv")
    frame_sha256 = hashlib.sha256(frame_path.read_bytes()).hexdigest()
    summary["candidate_frame_sha256"] = frame_sha256
    private_path = write_jsonl(private_cases, private / "restricted_cpt_cases.jsonl")
    private_sha256 = hashlib.sha256(private_path.read_bytes()).hexdigest()
    summary["private_packet_sha256"] = private_sha256
    (derived / "candidate_frame_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    redacted_cases = [
        {
            "schema_version": "mapping-blind-review-case-v2",
            "candidate_frame_sha256": frame_sha256,
            "case_id": row["case_id"],
            "family": row["family"],
            "target_relation": row["target_relation"],
            "evidence_location": (
                "ignored_local_packet"
                if row["right_source_id"] == "us_cms_pfs_local_cpt"
                else "reviewed_public_bundle"
            ),
            "private_packet_sha256": (
                private_sha256 if row["right_source_id"] == "us_cms_pfs_local_cpt" else None
            ),
            "left_code": row["left_code"],
            "right_code": row["right_code"],
            "allowed_decisions": ["positive", "negative", "exclude", "uncertain"],
        }
        for row in frame
    ]
    role_hashes: dict[str, str] = {}
    for role in ("reviewer_a", "reviewer_b"):
        path = write_jsonl(redacted_cases, packets / f"{role}_cases.jsonl")
        role_hashes[role] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {
        "schema_version": "mapping-blind-review-packet-manifest-v2",
        "study_cycle": OUTPUT_CYCLE,
        "status": "ready",
        "candidate_frame_sha256": frame_sha256,
        "case_count": len(frame),
        "private_case_count": len(private_cases),
        "private_packet_sha256": private_sha256,
        "role_packet_sha256": role_hashes,
        "role_packets_identical": len(set(role_hashes.values())) == 1,
        "hypotheses_exposed": False,
        "split_assignment_exposed": False,
        "descriptor_storage": "ignored_local_only",
    }
    (packets / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    """Freeze the private-enriched mapping cycle."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-cycle",
        default="expansion_v8",
    )
    args = parser.parse_args()
    root = project_root()
    base = _jsonl(root / "data/derived/mapping_study" / args.base_cycle / "candidate_frame.jsonl")
    local = _jsonl(root / "data/local/mapping_study/cpt_enrichment/candidates.jsonl")
    cpt_summary = json.loads(
        (root / "data/derived/mapping_study/local_cpt_enrichment_summary.json").read_text(
            encoding="utf-8"
        )
    )
    frame, private_cases, summary = build_enriched_cycle(
        base_frame=base,
        local_cpt_candidates=local,
        mbs_bundle_sha256=str(cpt_summary["mbs_bundle_sha256"]),
        cpt_archive_sha256=str(cpt_summary["source"]["archive_sha256"]),
    )
    private_cases = expand_private_cases(root, frame, private_cases)
    summary["private_case_count"] = len(private_cases)
    write_enriched_cycle(root, frame, private_cases, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

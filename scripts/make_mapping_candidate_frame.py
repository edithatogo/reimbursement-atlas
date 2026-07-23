"""Build a deterministic mapping candidate frame from reviewed derived bundles."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.crosswalk import jaccard_similarity, tokenise
from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.registry import project_root

OUTPUT_DIR = Path("data/derived/mapping_study")
FRAME_TARGETS = {
    "procedures_pathology": 600,
    "medicines": 400,
    "genomics_coverage": 300,
    "devices_other": 200,
}
SOURCE_FAMILIES = {
    "procedures_pathology": (
        {"au_mbs"},
        {"us_cms_clfs", "us_cms_pfs", "us_cms_hcpcs_level_ii"},
    ),
    "medicines": ({"au_pbs"}, {"atc", "rxnorm", "us_cms_asp"}),
    "genomics_coverage": ({"au_mbs", "uk_genomic_test_directory"}, {"loinc", "hpo"}),
    "devices_other": (
        {"au_mbs", "au_pbs"},
        {"gmdn", "umdns", "snomed_ct_device", "us_fda_device_classification"},
    ),
}


def build_candidate_frame(root: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Return candidate hypotheses and a fail-closed family coverage summary."""
    records, source_checksums = _load_reviewed_schedule_records(root)
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_source[str(row["source_id"])].append(row)

    frame: list[dict[str, object]] = []
    family_summary: dict[str, dict[str, object]] = {}
    for family, target in FRAME_TARGETS.items():
        left_sources, right_sources = SOURCE_FAMILIES[family]
        left = [row for source in sorted(left_sources) for row in by_source.get(source, [])]
        right = [row for source in sorted(right_sources) for row in by_source.get(source, [])]
        candidates = _family_candidates(
            family,
            left,
            right,
            source_checksums=source_checksums,
            limit=target,
        )
        frame.extend(candidates)
        family_summary[family] = {
            "target": target,
            "available": len(candidates),
            "gap": max(0, target - len(candidates)),
            "left_records": len(left),
            "right_records": len(right),
            "status": "ready" if len(candidates) >= target else "blocked_source_family",
        }

    frame = sorted(frame, key=lambda row: str(row["case_id"]))
    duplicate_groups = {str(row["duplicate_group"]) for row in frame}
    summary: dict[str, object] = {
        "schema_version": "mapping-candidate-frame-summary-v1",
        "status": (
            "ready_for_blinded_review"
            if all(item["status"] == "ready" for item in family_summary.values())
            else "blocked_source_families"
        ),
        "target_count": sum(FRAME_TARGETS.values()),
        "candidate_count": len(frame),
        "target_gap": max(0, sum(FRAME_TARGETS.values()) - len(frame)),
        "effective_unique_groups": len(duplicate_groups),
        "family_summary": family_summary,
        "fixture_rows_used": 0,
        "review_blinded": True,
        "split_assigned": False,
    }
    return frame, summary


def write_candidate_frame(
    root: Path,
    rows: list[dict[str, object]],
    summary: dict[str, object],
    *,
    output_dir: Path = OUTPUT_DIR,
) -> None:
    """Write deterministic frame rows and summary."""
    output = root / output_dir
    output.mkdir(parents=True, exist_ok=True)
    write_jsonl(rows, output / "candidate_frame.jsonl")
    write_csv(rows, output / "candidate_frame.csv")
    frame_path = output / "candidate_frame.jsonl"
    summary["candidate_frame_sha256"] = hashlib.sha256(frame_path.read_bytes()).hexdigest()
    (output / "candidate_frame_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _load_reviewed_schedule_records(
    root: Path,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    records: dict[tuple[str, str, str], dict[str, Any]] = {}
    checksums: dict[str, str] = {}
    bundle_root = root / "data/derived/reviewed_source_bundles"
    for path in sorted(bundle_root.glob("**/*schedule_items.jsonl")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = cast("dict[str, Any]", json.loads(line))
            raw_provenance = row.get("provenance")
            provenance = (
                cast("dict[str, Any]", raw_provenance) if isinstance(raw_provenance, dict) else {}
            )
            source_id = str(row.get("source_id", ""))
            code = str(row.get("item_code", ""))
            version = str(provenance.get("source_version", ""))
            if not source_id or not code or not version:
                continue
            key = (source_id, code, version)
            records[key] = row
            checksums[f"{source_id}:{version}"] = digest
    return list(records.values()), checksums


def _family_candidates(  # ruff:ignore[too-many-locals]
    family: str,
    left_rows: list[dict[str, Any]],
    right_rows: list[dict[str, Any]],
    *,
    source_checksums: dict[str, str],
    limit: int,
) -> list[dict[str, object]]:
    if not left_rows or not right_rows:
        return []
    right_tokens = [set(tokenise(_text(row))) for row in right_rows]
    token_index: dict[str, set[int]] = defaultdict(set)
    for index, tokens in enumerate(right_tokens):
        for token in tokens:
            token_index[token].add(index)
    candidates: list[tuple[float, dict[str, Any], dict[str, Any], str]] = []
    ordered_left = sorted(
        left_rows,
        key=lambda row: hashlib.sha256(
            f"{family}|{row.get('source_id')}|{row.get('item_code')}".encode()
        ).hexdigest(),
    )[:limit]
    for left in ordered_left:
        left_tokens = set(tokenise(_text(left)))
        rare_tokens = sorted(
            (token for token in left_tokens if token in token_index),
            key=lambda token: (len(token_index[token]), token),
        )[:3]
        matching_indices: set[int] = set()
        for token in rare_tokens:
            matching_indices.update(token_index[token])
        if not matching_indices:
            matching_indices = {_stable_index(left, len(right_rows))}
        elif len(matching_indices) > 512:
            matching_indices = set(sorted(matching_indices)[:512])
        scored = sorted(
            (
                (jaccard_similarity(left_tokens, right_tokens[index]), right_rows[index])
                for index in matching_indices
            ),
            key=lambda item: (-item[0], str(item[1]["source_id"]), str(item[1]["item_code"])),
        )
        if scored:
            negative_index = _negative_index(left, left_tokens, right_tokens)
            candidates.extend((
                (scored[0][0], left, scored[0][1], "positive_candidate"),
                (
                    jaccard_similarity(left_tokens, right_tokens[negative_index]),
                    left,
                    right_rows[negative_index],
                    "negative_candidate",
                ),
            ))
    rows = [
        _candidate_row(family, score, left, right, hypothesis, source_checksums)
        for score, left, right, hypothesis in candidates
    ]
    unique = {str(row["case_id"]): row for row in rows}
    positive = sorted(
        (
            row
            for row in unique.values()
            if row["proposed_label_hypothesis"] == "positive_candidate"
        ),
        key=lambda row: str(row["case_id"]),
    )
    negative = sorted(
        (
            row
            for row in unique.values()
            if row["proposed_label_hypothesis"] == "negative_candidate"
        ),
        key=lambda row: str(row["case_id"]),
    )
    selected = [*positive[: limit // 2], *negative[: limit - (limit // 2)]]
    if len(selected) < limit:
        selected_ids = {str(row["case_id"]) for row in selected}
        remainder = sorted(
            (row for row in unique.values() if str(row["case_id"]) not in selected_ids),
            key=lambda row: str(row["case_id"]),
        )
        selected.extend(remainder[: limit - len(selected)])
    return sorted(selected, key=lambda row: str(row["case_id"]))


def _stable_index(row: dict[str, Any], count: int) -> int:
    identity = f"{row.get('source_id')}|{row.get('item_code')}"
    return int(hashlib.sha256(identity.encode()).hexdigest()[:16], 16) % count


def _negative_index(
    row: dict[str, Any], left_tokens: set[str], right_tokens: list[set[str]]
) -> int:
    start = _stable_index(row, len(right_tokens))
    for offset in range(min(len(right_tokens), 256)):
        index = (start + offset) % len(right_tokens)
        if left_tokens.isdisjoint(right_tokens[index]):
            return index
    return start


def _candidate_row(
    family: str,
    score: float,
    left: dict[str, Any],
    right: dict[str, Any],
    hypothesis: str,
    source_checksums: dict[str, str],
) -> dict[str, object]:
    left_provenance = left["provenance"]
    right_provenance = right["provenance"]
    identity = "|".join((
        family,
        str(left["source_id"]),
        str(left["item_code"]),
        str(right["source_id"]),
        str(right["item_code"]),
    ))
    duplicate_identity = "|".join(sorted((_normalised_text(left), _normalised_text(right))))
    left_key = f"{left['source_id']}:{left_provenance['source_version']}"
    right_key = f"{right['source_id']}:{right_provenance['source_version']}"
    return {
        "schema_version": "mapping-candidate-frame-v1",
        "case_id": f"map_{hashlib.sha256(identity.encode()).hexdigest()[:20]}",
        "family": family,
        "left_source_id": left["source_id"],
        "left_code": left["item_code"],
        "right_source_id": right["source_id"],
        "right_code": right["item_code"],
        "source_versions": [left_provenance["source_version"], right_provenance["source_version"]],
        "provenance_checksums": [source_checksums[left_key], source_checksums[right_key]],
        "evidence_fields": ["item_code", "item_label", "item_description", "domain"],
        "proposed_label_hypothesis": hypothesis,
        "proposed_difficulty": "routine"
        if score >= 0.7
        else "hard"
        if score <= 0.1
        else "ambiguous",
        "duplicate_group": hashlib.sha256(duplicate_identity.encode()).hexdigest()[:16],
    }


def _text(row: dict[str, Any]) -> str:
    return " ".join(
        str(row.get(field) or "") for field in ("item_label", "item_description", "domain")
    )


def _normalised_text(row: dict[str, Any]) -> str:
    return " ".join(sorted(tokenise(_text(row))))


def main() -> None:
    """Write the current real-source mapping candidate frame and summary."""
    root = project_root()
    rows, summary = build_candidate_frame(root)
    output_dir = OUTPUT_DIR
    frozen_frame = root / OUTPUT_DIR / "candidate_frame.jsonl"
    blind_reviews = root / "data/mapping_study/blind_reviews.jsonl"
    if frozen_frame.exists() and blind_reviews.exists():
        candidate_bytes = "".join(
            json.dumps(row, sort_keys=True, default=str) + "\n" for row in rows
        ).encode()
        if (
            hashlib.sha256(candidate_bytes).digest()
            != hashlib.sha256(frozen_frame.read_bytes()).digest()
        ):
            output_dir = OUTPUT_DIR / "expansion_v2"
            summary["schema_version"] = "mapping-candidate-frame-summary-v2"
            summary["study_cycle"] = "expansion_v2"
            summary["immutable_predecessor_sha256"] = hashlib.sha256(
                frozen_frame.read_bytes()
            ).hexdigest()
    write_candidate_frame(root, rows, summary, output_dir=output_dir)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "candidate_count": len(rows),
                "target_gap": summary["target_gap"],
                "output_dir": str(output_dir),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

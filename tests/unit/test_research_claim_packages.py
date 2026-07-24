from __future__ import annotations

import json
import shutil
from pathlib import Path

from reimburse_atlas.research_claim_packages import (
    build_claim_package_candidates,
    write_claim_package_candidates,
)


def test_claim_packages_are_fail_closed_and_use_reviewed_inputs() -> None:
    root = Path(__file__).resolve().parents[2]
    packages = build_claim_package_candidates(root)

    assert len(packages) == 5
    assert all(row["claim_approval_status"] == "pending_accountable_review" for row in packages)
    assert all(row["validation"]["raw_payloads_included"] is False for row in packages)
    transparency = next(
        row for row in packages if row["research_question_id"] == "rq_source_transparency"
    )
    assert transparency["analysis_status"] == "complete"
    assert transparency["descriptive_results"]["source_count"] > 0


def test_claim_package_generation_is_deterministic() -> None:
    root = Path(__file__).resolve().parents[2]
    first = build_claim_package_candidates(root)
    second = build_claim_package_candidates(root)
    assert first == second


def test_claim_package_writer_emits_checksum_bound_summary(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    for relative in (
        "data/seed/source_registry.jsonl",
        "data/derived/mapping_study/expansion_v9/evaluation_summary.json",
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / relative, target)
    source_bundle = next(
        (root / "data/derived/reviewed_source_bundles").glob("*/source_snapshots.jsonl")
    )
    target_bundle = (
        tmp_path
        / "data/derived/reviewed_source_bundles"
        / source_bundle.parent.name
        / source_bundle.name
    )
    target_bundle.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_bundle, target_bundle)

    paths = write_claim_package_candidates(tmp_path)
    summary = json.loads(paths[-1].read_text(encoding="utf-8"))

    assert len(paths) == 6
    assert summary["package_count"] == 5
    assert summary["complete_count"] == 1
    assert summary["pending_accountable_review_count"] == 5
    assert all(len(row["sha256"]) == 64 for row in summary["packages"])

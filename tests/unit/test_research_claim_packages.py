from __future__ import annotations

import hashlib
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
    assert all(row["validation"]["raw_payloads_included"] is False for row in packages)
    transparency = next(
        row for row in packages if row["research_question_id"] == "rq_source_transparency"
    )
    assert transparency["analysis_status"] == "complete"
    assert transparency["claim_approval_status"] == "pending_accountable_review"
    assert transparency["descriptive_results"]["source_count"] > 0
    assert all(row["analysis_status"] == "complete" for row in packages)
    genomics = next(
        row for row in packages if row["research_question_id"] == "rq_genomics_coverage_price"
    )
    assert genomics["missing_reviewed_sources"] == []
    assert genomics["claim_approval_status"] == "pending_accountable_review"


def test_claim_package_generation_is_deterministic() -> None:
    root = Path(__file__).resolve().parents[2]
    first = build_claim_package_candidates(root)
    second = build_claim_package_candidates(root)
    assert first == second


def test_repository_claim_summary_recognises_checksum_bound_approvals() -> None:
    root = Path(__file__).resolve().parents[2]
    summary = json.loads(
        (root / "data/derived/research_claims/summary.json").read_text(encoding="utf-8")
    )

    assert summary["approved_within_scope_count"] == 5
    assert summary["pending_accountable_review_count"] == 0


def test_claim_package_writer_emits_checksum_bound_summary(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    for relative in (
        "data/seed/source_registry.jsonl",
        "data/seed/research_questions.jsonl",
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
    assert summary["reviewable_count"] == 1
    assert summary["pending_accountable_review_count"] == 1
    assert summary["partial_source_gap_count"] == 4
    assert all(len(row["sha256"]) == 64 for row in summary["packages"])
    reports = sorted((tmp_path / "reports").glob("*.md"))
    assert len(reports) == 5
    assert all("not a paper or preprint" in path.read_text(encoding="utf-8") for path in reports)

    package = paths[0]
    package_relative = package.relative_to(tmp_path).as_posix()
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    review_relative = "data/research_claims/reviews/approved.json"
    review = tmp_path / review_relative
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(
        json.dumps({
            "status": "approved_within_scope",
            "claim_package_path": package_relative,
            "claim_package_sha256": digest,
        }),
        encoding="utf-8",
    )
    decisions = tmp_path / "data/research_claims/decisions.jsonl"
    decisions.parent.mkdir(parents=True, exist_ok=True)
    decisions.write_text(
        json.dumps({
            "status": "approved_within_scope",
            "reviewed_derived_inputs": True,
            "analysis_validated": True,
            "claim_package_path": package_relative,
            "claim_package_sha256": digest,
            "review_record": review_relative,
        })
        + "\n",
        encoding="utf-8",
    )

    refreshed = write_claim_package_candidates(tmp_path)
    refreshed_summary = json.loads(refreshed[-1].read_text(encoding="utf-8"))
    assert refreshed_summary["approved_within_scope_count"] == 1

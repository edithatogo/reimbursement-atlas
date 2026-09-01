"""Tests for deterministic medallion evidence projection."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from reimburse_atlas.medallion_projection import (
    build_bronze_projections,
    build_gold_artifacts,
    build_platinum_artifacts,
    build_promotion_decisions,
    build_silver_artifacts,
    materialise_medallion_projection,
)
from reimburse_atlas.release_readiness import build_release_readiness_report


def _write_jsonl(path: Path, rows: list[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def _fixture_root(tmp_path: Path) -> Path:
    source_file = {
        "id": "source_file",
        "source_id": "source",
        "source_version_id": "source_v1",
        "source_url": "https://example.gov/source.csv",
        "expected_format": "CSV",
        "licence_gate": "public_reuse_review",
    }
    validation = {
        "source_file_id": "source_file",
        "validation_status": "pass",
        "checksum_sha256": "a" * 64,
        "byte_size": 10,
    }
    _write_jsonl(tmp_path / "data/seed/source_files.jsonl", [source_file])
    _write_jsonl(
        tmp_path / "data/seed/source_registry.jsonl",
        [
            {
                "id": "source",
                "primary_url": "https://example.gov/source.csv",
                "format": "CSV",
            }
        ],
    )
    _write_jsonl(
        tmp_path / "data/derived/source_validation/source_content_validation.jsonl",
        [validation],
    )
    report_path = (
        tmp_path / "data/derived/reviewed_source_bundles/bundle_source/validation_report.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps({"checksum_sha256": "a" * 64, "licence_gate": "public_reuse_review"}),
        encoding="utf-8",
    )
    mapping = tmp_path / "data/derived/mapping_study/expansion_v9/evaluation_summary.json"
    mapping.parent.mkdir(parents=True, exist_ok=True)
    mapping.write_text(json.dumps({"status": "accepted", "evaluated_once": True}), encoding="utf-8")
    evidence = tmp_path / "data/derived/evidence_readiness/summary.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(
        json.dumps({"research_question_count": 1, "evidence_ready": 0, "blocked": 1}),
        encoding="utf-8",
    )
    _write_jsonl(tmp_path / "data/licence_review/decisions.jsonl", [])
    products = (
        tmp_path / "pyproject.toml",
        tmp_path / "apps/dashboard/src/pages/sources/index.astro",
        tmp_path / ".zenodo.json",
    )
    for product in products:
        product.parent.mkdir(parents=True, exist_ok=True)
        product.write_text("{}\n", encoding="utf-8")
    return tmp_path


def test_projection_is_deterministic_and_fail_closed(tmp_path: Path) -> None:
    """Repeated generation is stable and Platinum stays blocked upstream."""
    root = _fixture_root(tmp_path)
    first = materialise_medallion_projection(root)
    first_hash = hashlib.sha256(
        (root / "data/derived/medallion/promotion_decisions.jsonl").read_bytes()
    ).hexdigest()
    second = materialise_medallion_projection(root)
    second_hash = hashlib.sha256(
        (root / "data/derived/medallion/promotion_decisions.jsonl").read_bytes()
    ).hexdigest()
    assert first == second
    assert first_hash == second_hash
    assert first.bronze_b0_count == 1
    assert first.bronze_b2_count == 1
    assert first.platinum_approved_count == 0
    assert first.evidence_release_ready is False


def test_projection_omits_raw_paths(tmp_path: Path) -> None:
    """Shareable medallion evidence contains identity, never raw cache paths."""
    root = _fixture_root(tmp_path)
    materialise_medallion_projection(root)
    for path in (root / "data/derived/medallion").glob("*.jsonl"):
        assert "raw_live" not in path.read_text(encoding="utf-8")


def test_projection_uses_canonical_release_readiness(tmp_path: Path) -> None:
    """A partial evidence summary cannot contradict the complete gate matrix."""
    root = _fixture_root(tmp_path)
    (root / "data/derived/evidence_readiness/summary.json").write_text(
        json.dumps({"research_question_count": 1, "evidence_ready": 1, "blocked": 0}),
        encoding="utf-8",
    )

    medallion = materialise_medallion_projection(root)
    release = build_release_readiness_report(root)

    assert medallion.evidence_release_ready is False
    assert medallion.evidence_release_ready == release.summary.evidence_release_ready


def test_committed_medallion_and_release_summaries_share_readiness() -> None:
    """Checked-in public summaries must never expose contradictory readiness."""
    medallion = json.loads(Path("data/derived/medallion/summary.json").read_text(encoding="utf-8"))
    release = json.loads(
        Path("data/derived/release_readiness/summary.json").read_text(encoding="utf-8")
    )

    assert medallion["evidence_release_ready"] == release["evidence_release_ready"]


def test_source_transparency_has_one_bounded_platinum_promotion(  # ruff: ignore[too-many-locals]
    tmp_path: Path,
) -> None:
    """A current scoped contract promotes one product without global readiness."""
    root = _fixture_root(tmp_path)
    registry = root / "data/seed/source_registry.jsonl"
    registry_sha = hashlib.sha256(registry.read_bytes()).hexdigest()
    claim = root / "data/derived/research_claims/rq_source_transparency.json"
    claim.parent.mkdir(parents=True, exist_ok=True)
    claim.write_text(
        json.dumps({"descriptive_results": {"input_sha256": registry_sha}}) + "\n",
        encoding="utf-8",
    )
    claim_sha = hashlib.sha256(claim.read_bytes()).hexdigest()
    review = root / "data/research_claims/source_transparency_review.json"
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(
        json.dumps({
            "status": "approved_within_scope",
            "claim_package_path": claim.relative_to(root).as_posix(),
            "claim_package_sha256": claim_sha,
            "reviewed_derived_inputs": True,
            "analysis_validated": True,
        })
        + "\n",
        encoding="utf-8",
    )
    review_sha = hashlib.sha256(review.read_bytes()).hexdigest()
    product = root / "apps/dashboard/src/pages/sources/index.astro"
    product_sha = hashlib.sha256(product.read_bytes()).hexdigest()
    contract = root / "data/product_release/contracts/source_transparency_dashboard.json"
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text(
        json.dumps({
            "schema_version": "platinum-release-contract-v1",
            "contract_id": "platinum-source-transparency-dashboard-v1",
            "product_id": "source-transparency-dashboard",
            "product_path": product.relative_to(root).as_posix(),
            "product_sha256": product_sha,
            "public_route": "/sources",
            "gold_artifact_id": "gold:source-transparency-claim-package",
            "source_registry_path": registry.relative_to(root).as_posix(),
            "source_registry_sha256": registry_sha,
            "claim_package_path": claim.relative_to(root).as_posix(),
            "claim_package_sha256": claim_sha,
            "claim_review_path": review.relative_to(root).as_posix(),
            "claim_review_sha256": review_sha,
            "approval_scope": "Metadata observations only.",
            "required_gate_ids": [
                "gold_input_approved",
                "repository_release_ready",
                "public_data_policy_passed",
                "product_rights_approved",
                "scoped_claim_review_current",
            ],
            "prohibited_claims": ["causal claims", "papers or preprints"],
            "rights_state": "permissive",
        })
        + "\n",
        encoding="utf-8",
    )
    _write_jsonl(
        root / "data/derived/local_quality_gates/local_quality_gates.jsonl",
        [{"id": "public_data_policy", "status": "passed", "return_code": 0}],
    )

    b0, b1, b2 = build_bronze_projections(root)
    silver = build_silver_artifacts(root)
    gold = build_gold_artifacts(root, silver)
    platinum = build_platinum_artifacts(
        root,
        gold,
        evidence_release_ready=False,
        repository_release_ready=True,
    )
    decisions = build_promotion_decisions(
        root,
        b0,
        b1,
        b2,
        silver,
        gold,
        platinum,
        evidence_release_ready=False,
        repository_release_ready=True,
    )

    assert sum(row.promotion_status == "approved_within_scope" for row in platinum) == 1
    approved = next(row for row in platinum if row.promotion_status == "approved_within_scope")
    assert approved.relative_path == product.relative_to(root).as_posix()
    promotion = next(row for row in decisions if row.subject_id == approved.artifact_id)
    assert promotion.status == "approved"
    assert promotion.required_gate_ids == promotion.passed_gate_ids

    product.write_text("changed\n", encoding="utf-8")
    stale = build_platinum_artifacts(
        root,
        gold,
        evidence_release_ready=False,
        repository_release_ready=True,
    )
    assert all(row.promotion_status != "approved_within_scope" for row in stale)


def test_bronze_projection_admits_real_receipts_without_raw_paths(tmp_path: Path) -> None:
    """Reviewed and historical receipts expand B1/B2 without exposing local caches."""
    root = _fixture_root(tmp_path)
    _write_jsonl(
        root / "data/derived/reviewed_source_bundles/reviewed/source_snapshots.jsonl",
        [
            {
                "id": "reviewed_snapshot",
                "source_id": "source",
                "source_version_id": "source_reviewed",
                "source_url": "https://example.gov/reviewed.csv",
                "retrieved_at": "2026-08-01T00:00:00Z",
                "checksum_sha256": "b" * 64,
                "byte_size": 20,
                "content_type": "text/csv",
                "licence_gate": "permissive",
                "local_path": "/private/raw/reviewed.csv",
            }
        ],
    )
    _write_jsonl(
        root / "data/derived/historical_sources/historical_source_downloads.jsonl",
        [
            {
                "id": "historical_acquired",
                "source_id": "source",
                "source_version_id": "source_2025",
                "source_url": "https://example.gov/2025.csv",
                "status": "downloaded",
                "checksum_sha256": "c" * 64,
                "byte_size": 30,
                "file_kind": "csv",
                "licence_gate": "public_reuse_review",
                "review_status": "pending_human_review",
                "cache_path": "data/raw_live/historical/source.csv",
            },
            {
                "id": "historical_failed",
                "source_id": "source",
                "source_version_id": "source_2024",
                "source_url": "https://example.gov/2024.csv",
                "status": "download_failed",
                "checksum_sha256": None,
                "byte_size": None,
                "file_kind": "csv",
                "licence_gate": "public_reuse_review",
                "review_status": "pending_human_review",
                "cache_path": "data/raw_live/historical/missing.csv",
            },
        ],
    )
    summary = root / "data/derived/historical_sources/historical_source_downloads_summary.json"
    summary.write_text(json.dumps({"generated_at": "2026-08-02T00:00:00Z"}), encoding="utf-8")

    b0, b1, b2 = build_bronze_projections(root)

    assert len(b1) == 4
    assert len(b2) == 3
    assert sum(row.outcome == "acquired" for row in b1) == 3
    assert sum(row.outcome == "failed" for row in b1) == 1
    assert b0[0].acquisition_status == "acquired"
    payload = json.dumps([row.model_dump(mode="json") for row in [*b1, *b2]])
    assert "raw_live" not in payload
    assert "/private/" not in payload

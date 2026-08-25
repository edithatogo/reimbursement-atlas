"""Tests for deterministic medallion evidence projection."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from reimburse_atlas.medallion_projection import materialise_medallion_projection


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
        tmp_path / "apps/dashboard/package-lock.json",
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

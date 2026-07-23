"""Tests for the optional human-review JSON Schema contracts."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.validate_review_schemas import validate_review_file, validate_root_jsonl_review


def test_empty_review_files_are_valid(tmp_path: Path) -> None:
    """No decision file means pending review, not implicit approval."""
    for review_dir in ("licence_review", "mapping_review"):
        directory = tmp_path / "data" / review_dir
        directory.mkdir(parents=True)
        source = Path("data") / review_dir / "decision.schema.json"
        (directory / "decision.schema.json").write_text(
            source.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        assert (
            validate_review_file(tmp_path, review_dir, "decision.schema.json", "decisions.jsonl")
            == []
        )


def test_mapping_review_schema_rejects_out_of_range_confidence(tmp_path: Path) -> None:
    """A recorded decision cannot contain an invalid machine confidence."""
    directory = tmp_path / "data" / "mapping_review"
    directory.mkdir(parents=True)
    source = Path("data/mapping_review/decision.schema.json")
    (directory / "decision.schema.json").write_text(
        source.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (directory / "decisions.jsonl").write_text(
        json.dumps({
            "review_id": "mapping_1",
            "left_source_id": "au_mbs",
            "right_source_id": "us_cms_clfs",
            "left_code": "73358",
            "right_code": "81479",
            "candidate_relationship": "related",
            "candidate_confidence": 1.1,
            "decision": "deferred",
            "reviewer": "Reviewer",
            "reviewer_role": "domain reviewer",
            "reviewed_at": "2026-07-17",
            "relationship_decision": "related",
            "scope_equivalence": "pending",
            "unit_equivalence": "pending",
            "evidence": "source record",
            "rationale": "Needs review",
        })
        + "\n",
        encoding="utf-8",
    )

    errors = validate_review_file(
        tmp_path, "mapping_review", "decision.schema.json", "decisions.jsonl"
    )
    assert any("candidate_confidence" in error for error in errors)


def test_cycle_review_file_uses_root_mapping_schema(tmp_path: Path) -> None:
    schema = Path("schema/MappingBlindReviewRecord.schema.json")
    target = tmp_path / schema
    target.parent.mkdir(parents=True)
    target.write_text(schema.read_text(encoding="utf-8"), encoding="utf-8")
    review = tmp_path / "data/mapping_study/expansion_v2/blind_reviews.jsonl"
    review.parent.mkdir(parents=True)
    review.write_text('{"schema_version":"wrong"}\n', encoding="utf-8")

    errors = validate_root_jsonl_review(
        tmp_path,
        schema.as_posix(),
        "data/mapping_study/expansion_v2/blind_reviews.jsonl",
    )

    assert errors

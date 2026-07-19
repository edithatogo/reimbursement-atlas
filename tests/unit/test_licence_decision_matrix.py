"""Tests for grouped licence decisions and reproducibility boundaries."""

from pathlib import Path

from scripts.make_licence_decision_matrix import build_matrix, render_markdown


def test_matrix_covers_source_families_and_fail_closed_status() -> None:
    matrix = build_matrix(Path(__file__).parents[2])
    groups = {group["id"]: group for group in matrix["groups"]}
    assert groups["code_and_documentation"]["status"] == "decided"
    assert groups["au_mbs"]["status"] == "pending_human_review"
    assert groups["us_cms"]["source_record_count"] > 0
    assert groups["us_cms"]["release_gate"] == "human_licence_review"
    assert "checksum-bound" in matrix["approval_rule"]


def test_matrix_tolerates_missing_optional_catalogue(tmp_path: Path) -> None:
    matrix = build_matrix(tmp_path)
    groups = {group["id"]: group for group in matrix["groups"]}
    assert matrix["source_catalogue_counts"] == {}
    assert groups["us_cms"]["source_record_count"] == 0


def test_markdown_references_provenance_and_transformation_artifacts() -> None:
    markdown = render_markdown(build_matrix(Path(__file__).parents[2]))
    assert "SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md" in markdown
    assert "historical_source_transformation.bpmn" in markdown
    assert "licence_review_queue.jsonl" in markdown

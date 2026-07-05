"""v16 tests for source validation, data quality and research linkages."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.data_quality import build_data_quality_checks
from reimburse_atlas.models import SourceFileRecord
from reimburse_atlas.registry import (
    load_dataset_candidates,
    load_mapping_resources,
    load_output_artifact_plans,
    load_research_questions,
    load_source_files,
    load_source_registry,
)
from reimburse_atlas.roadmap_linkages import build_research_linkages
from reimburse_atlas.source_downloads import safe_local_target
from reimburse_atlas.source_validation import build_source_content_validations


def test_source_content_validation_reports_missing_downloads(tmp_path: Path) -> None:
    """Executable source records are marked missing before networked acquisition."""
    records = load_source_files()
    rows = build_source_content_validations(records, raw_dir=tmp_path)
    by_id = {row.source_file_id: row for row in rows}
    assert by_id["au_mbs_20260701_imap_txt"].validation_status == "missing"
    assert by_id["us_cms_clfs_26clabq3_page"].validation_status == "skipped"
    assert all(not row.local_target_ref.startswith("/") for row in rows)


def test_source_content_validation_accepts_local_txt_fixture(tmp_path: Path) -> None:
    """A local TXT source validates without exposing its absolute path."""
    record = SourceFileRecord.model_validate(load_source_files()[0].model_dump(mode="json"))
    target = safe_local_target(record, tmp_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("item|group|fee\n1|A|12.30\n2|A|15.50\n", encoding="utf-8")
    rows = build_source_content_validations([record], raw_dir=tmp_path)
    assert rows[0].validation_status == "pass"
    assert rows[0].observed_record_count == 2
    assert rows[0].checksum_sha256 is not None
    assert rows[0].local_target_ref == f"local_raw_only:{record.source_id}/{target.name}"


def test_data_quality_checks_have_no_blocking_failures_after_generation() -> None:
    """Core generated artefacts satisfy v16 quality expectations."""
    rows = build_data_quality_checks()
    blocking = [
        row for row in rows if row.severity == "blocking" and row.status in {"fail", "missing"}
    ]
    assert blocking == []
    assert any(row.id == "publication_manifest_raw_source_payload_absent" for row in rows)


def test_research_linkages_cover_questions_and_outputs() -> None:
    """Research questions are linked to datasets, mapping resources and publication outputs."""
    rows = build_research_linkages(
        research_questions=load_research_questions(),
        sources=load_source_registry(),
        dataset_candidates=load_dataset_candidates(),
        mapping_resources=load_mapping_resources(),
        output_plans=load_output_artifact_plans(),
    )
    question_ids = {row.research_question_id for row in rows}
    assert question_ids == {question.id for question in load_research_questions()}
    assert any(row.linked_entity_type == "mapping_resource" for row in rows)
    assert any(row.linked_entity_type == "output" for row in rows)
    assert not [row for row in rows if row.readiness_status == "missing"]

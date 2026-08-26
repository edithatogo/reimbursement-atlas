from pathlib import Path

from reimburse_atlas.dataset_candidate_assessment import (
    build_dataset_candidate_assessments,
    write_dataset_candidate_assessments,
)
from reimburse_atlas.registry import load_dataset_candidates, load_source_registry


def test_all_candidates_have_bounded_metadata_assessments(tmp_path: Path) -> None:
    records = build_dataset_candidate_assessments(load_dataset_candidates(), load_source_registry())
    assert len(records) == 15
    assert all(record.issue_disposition == "close_metadata_onboarding" for record in records)
    assert all(record.acquisition_status == "not_acquired" for record in records)
    assert all(record.parser_status != "validated" for record in records)
    paths = write_dataset_candidate_assessments(records, output_dir=tmp_path)
    assert all(path.is_file() for path in paths)


def test_source_links_are_explicit_not_inferred_from_names() -> None:
    records = build_dataset_candidate_assessments(load_dataset_candidates(), load_source_registry())
    by_id = {record.candidate_id: record for record in records}
    assert by_id["ds_us_cms_mcd_downloads"].linked_source_ids == ("us_cms_mcd",)
    assert by_id["ds_us_hospital_price_transparency"].linked_source_ids == ()

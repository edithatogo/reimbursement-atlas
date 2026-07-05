"""Generate a local, no-network vertical-slice dataset from permissive fixtures."""

from __future__ import annotations

from reimburse_atlas.analysis import (
    build_crosswalk_candidates,
    build_mapping_evidence_matrix,
    median_payment_by_source,
    policy_signal_matrix,
    priced_share,
)
from reimburse_atlas.gold_standard import (
    build_gold_standard_set,
    build_mapping_calibration_cases,
    build_mapping_calibration_summary,
    build_negative_controls,
)
from reimburse_atlas.io import pydantic_rows, write_csv, write_jsonl
from reimburse_atlas.parsers import (
    parse_cms_asp_csv,
    parse_cms_clfs_csv,
    parse_cms_pfs_csv,
    parse_mbs_xml,
    parse_nhs_genomic_directory_csv,
    parse_pbs_csv,
)
from reimburse_atlas.registry import project_root
from reimburse_atlas.review_queue import build_crosswalk_review_queue, review_rows


def main() -> None:  # noqa: PLR0914
    """Parse local fixtures and write derived vertical-slice artefacts."""
    root = project_root()
    fixtures = root / "tests" / "fixtures"
    out = root / "data" / "derived" / "vertical_slice"

    mbs_records = parse_mbs_xml(fixtures / "mbs_fragment.xml")
    pbs_records = parse_pbs_csv(fixtures / "pbs_fixture.csv")
    clfs_records = parse_cms_clfs_csv(fixtures / "cms_clfs_fixture.csv")
    pfs_records = parse_cms_pfs_csv(fixtures / "cms_pfs_fixture.csv")
    asp_records = parse_cms_asp_csv(fixtures / "cms_asp_fixture.csv")
    coverage_records = parse_nhs_genomic_directory_csv(
        fixtures / "nhs_genomic_directory_fixture.csv"
    )
    schedule_records = [*mbs_records, *pbs_records, *clfs_records, *pfs_records, *asp_records]
    crosswalks = build_crosswalk_candidates(mbs_records, clfs_records, threshold=0.05)
    review_queue = build_crosswalk_review_queue(crosswalks)
    policy_rows = median_payment_by_source(schedule_records)
    priced_rows = [
        {"source_id": source_id, "priced_share": share}
        for source_id, share in priced_share(schedule_records).items()
    ]
    signal_rows = policy_signal_matrix(schedule_records, coverage_records)
    mapping_rows = build_mapping_evidence_matrix(
        mbs_records,
        [*clfs_records, *pfs_records],
        threshold=0.05,
    )
    gold_standard_rows = build_gold_standard_set()
    negative_control_rows = build_negative_controls()
    calibration_cases = build_mapping_calibration_cases(crosswalks)
    calibration_summary = build_mapping_calibration_summary(calibration_cases)

    write_jsonl(pydantic_rows(schedule_records), out / "schedule_items.jsonl")
    write_csv(pydantic_rows(schedule_records), out / "schedule_items.csv")
    write_jsonl(pydantic_rows(coverage_records), out / "coverage_decisions.jsonl")
    write_csv(pydantic_rows(coverage_records), out / "coverage_decisions.csv")
    write_jsonl(pydantic_rows(crosswalks), out / "crosswalk_candidates.jsonl")
    write_csv(pydantic_rows(crosswalks), out / "crosswalk_candidates.csv")
    write_jsonl(review_rows(review_queue), out / "crosswalk_review_queue.jsonl")
    write_csv(review_rows(review_queue), out / "crosswalk_review_queue.csv")
    write_csv(policy_rows, out / "median_payment_by_source.csv")
    write_jsonl(policy_rows, out / "median_payment_by_source.jsonl")
    write_csv(priced_rows, out / "priced_share.csv")
    write_jsonl(priced_rows, out / "priced_share.jsonl")
    write_csv(signal_rows, out / "policy_signal_matrix.csv")
    write_jsonl(signal_rows, out / "policy_signal_matrix.jsonl")
    write_csv(pydantic_rows(mapping_rows), out / "mapping_evidence_matrix.csv")
    write_jsonl(pydantic_rows(mapping_rows), out / "mapping_evidence_matrix.jsonl")
    write_csv(pydantic_rows(gold_standard_rows), out / "gold_standard_mappings.csv")
    write_jsonl(pydantic_rows(gold_standard_rows), out / "gold_standard_mappings.jsonl")
    write_csv(pydantic_rows(negative_control_rows), out / "negative_controls.csv")
    write_jsonl(pydantic_rows(negative_control_rows), out / "negative_controls.jsonl")
    write_csv(pydantic_rows(calibration_cases), out / "mapping_calibration_cases.csv")
    write_jsonl(pydantic_rows(calibration_cases), out / "mapping_calibration_cases.jsonl")
    calibration_summary_rows = [calibration_summary.model_dump(mode="json")]
    write_csv(calibration_summary_rows, out / "mapping_calibration_summary.csv")
    write_jsonl(calibration_summary_rows, out / "mapping_calibration_summary.jsonl")
    print(
        "Wrote vertical slice: "
        f"{len(schedule_records)} schedule items, "
        f"{len(coverage_records)} coverage decisions, "
        f"{len(crosswalks)} crosswalk candidates, "
        f"{len(review_queue)} review rows, "
        f"{len(signal_rows)} policy signal rows, "
        f"{len(mapping_rows)} mapping evidence rows, "
        f"{len(calibration_cases)} calibration cases"
    )


if __name__ == "__main__":
    main()

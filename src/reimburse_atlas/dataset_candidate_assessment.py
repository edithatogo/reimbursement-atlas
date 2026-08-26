"""Deterministic governance assessments for catalogued dataset candidates."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import DatasetCandidateRecord, SourceRecord

SOURCE_LINKS: dict[str, tuple[str, ...]] = {
    "ds_us_cms_mcd_downloads": ("us_cms_mcd",),
    "ds_oecd_health_statistics": ("oecd_health_stats",),
    "ds_who_ghed": ("who_gho",),
    "ds_brazil_sigtap": ("br_sigtap",),
    "ds_korea_hira": ("kr_hira",),
    "ds_singapore_moh_benchmarks": ("sg_fee_benchmarks",),
    "ds_aihw_health_expenditure": ("au_aihw_mbs_pbs_stats",),
}


@dataclass(frozen=True)
class DatasetCandidateAssessment:
    """One bounded candidate-onboarding decision."""

    candidate_id: str
    candidate_name: str
    source_url: str
    access_mode: str
    licence_gate: str
    linked_source_ids: tuple[str, ...]
    metadata_status: str
    acquisition_status: str
    parser_status: str
    issue_disposition: str
    scope_note: str
    next_step: str

    def as_row(self) -> dict[str, object]:
        """Return a serialization-safe row."""
        return asdict(self)


def build_dataset_candidate_assessments(
    candidates: list[DatasetCandidateRecord],
    sources: list[SourceRecord],
) -> tuple[DatasetCandidateAssessment, ...]:
    """Assess metadata onboarding without implying source acquisition."""
    source_ids = {source.id for source in sources}
    records: list[DatasetCandidateAssessment] = []
    for candidate in candidates:
        linked = SOURCE_LINKS.get(str(candidate.id), ())
        missing_links = sorted(set(linked) - source_ids)
        if missing_links:
            msg = f"Unknown source-registry links for {candidate.id}: {missing_links}"
            raise ValueError(msg)
        records.append(
            DatasetCandidateAssessment(
                candidate_id=str(candidate.id),
                candidate_name=candidate.name,
                source_url=str(candidate.source_url),
                access_mode=candidate.access_mode,
                licence_gate=candidate.licence_gate,
                linked_source_ids=linked,
                metadata_status="source_registered" if linked else "candidate_registered",
                acquisition_status="not_acquired",
                parser_status=candidate.parser_status,
                issue_disposition="close_metadata_onboarding",
                scope_note=(
                    "Candidate metadata and governance scope are registered. This does not "
                    "establish payload acquisition, parser validation, redistribution rights, "
                    "source completeness, or evidence readiness."
                ),
                next_step=candidate.recommended_next_step,
            )
        )
    return tuple(records)


def write_dataset_candidate_assessments(
    records: tuple[DatasetCandidateAssessment, ...], *, output_dir: Path
) -> tuple[Path, Path, Path]:
    """Write deterministic assessment evidence."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [record.as_row() for record in records]
    jsonl_path = write_jsonl(rows, output_dir / "dataset_candidate_assessments.jsonl")
    csv_path = write_csv(rows, output_dir / "dataset_candidate_assessments.csv")
    summary_path = output_dir / "summary.json"
    summary = {
        "schema_version": "dataset-candidate-assessment-v1",
        "candidate_count": len(records),
        "metadata_onboarded_count": sum(
            record.issue_disposition == "close_metadata_onboarding" for record in records
        ),
        "source_registered_count": sum(
            record.metadata_status == "source_registered" for record in records
        ),
        "acquired_count": sum(record.acquisition_status == "acquired" for record in records),
        "validated_parser_count": sum(record.parser_status == "validated" for record in records),
        "scope": "metadata_and_governance_only",
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return jsonl_path, csv_path, summary_path

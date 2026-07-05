"""Generate explicit research-question-to-dataset/mapping/output linkages."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import (
    DatasetCandidateRecord,
    MappingResourceRecord,
    OutputArtifactPlanRecord,
    ResearchLinkageRecord,
    ResearchQuestionRecord,
    SourceRecord,
)


def build_research_linkages(
    *,
    research_questions: list[ResearchQuestionRecord],
    sources: list[SourceRecord],
    dataset_candidates: list[DatasetCandidateRecord],
    mapping_resources: list[MappingResourceRecord],
    output_plans: list[OutputArtifactPlanRecord],
) -> list[ResearchLinkageRecord]:
    """Build linkage rows for roadmap, OSF and GitHub Project planning."""
    source_by_id = {record.id: record for record in sources}
    dataset_by_id = {record.id: record for record in dataset_candidates}
    output_by_track = _group_by_track(output_plans)
    mapping_by_topic = _mapping_resources_by_topic(mapping_resources)
    rows: list[ResearchLinkageRecord] = []
    for question in research_questions:
        for dataset_id in question.required_datasets:
            if dataset_id == "source_registry":
                rows.append(
                    _row(
                        question,
                        "source",
                        "source_registry",
                        "Source registry",
                        "required_metadata_registry",
                        "available",
                        "Use the source registry as the primary transparency-atlas dataset.",
                    )
                )
            elif dataset_id in source_by_id:
                source = source_by_id[dataset_id]
                rows.append(
                    _row(
                        question,
                        "source",
                        source.id,
                        f"{source.jurisdiction} — {source.schedule}",
                        "required_dataset",
                        "available",
                        (
                            "Use the registered source metadata and exact source-file "
                            "records where available."
                        ),
                    )
                )
            elif dataset_id in dataset_by_id:
                dataset = dataset_by_id[dataset_id]
                rows.append(
                    _row(
                        question,
                        "dataset_candidate",
                        dataset.id,
                        dataset.name,
                        "required_dataset_candidate",
                        "planned" if dataset.priority in {"must", "should"} else "blocked",
                        (
                            "Onboard this candidate through a source record, source-file "
                            "record and parser plan."
                        ),
                    )
                )
            else:
                rows.append(
                    _row(
                        question,
                        "dataset_candidate",
                        dataset_id,
                        dataset_id,
                        "unresolved_required_dataset",
                        "missing",
                        (
                            "Add a source-registry or dataset-candidate row before this "
                            "protocol can be complete."
                        ),
                    )
                )
        for mapping in mapping_by_topic.get(_topic_for_question(question), []):
            rows.append(
                _row(
                    question,
                    "mapping_resource",
                    mapping.id,
                    mapping.name,
                    "supporting_mapping_resource",
                    "local_only" if mapping.local_only else "planned",
                    "Implement a local/licence-aware adapter before using this in analysis.",
                )
            )
        for output in output_by_track.get(question.track_id, []):
            rows.append(
                _row(
                    question,
                    "output",
                    output.id,
                    f"{output.output_type} on {output.target_platform}",
                    "planned_output",
                    "available" if output.status in {"implemented", "published"} else "planned",
                    (
                        "Keep output plan aligned with release gates and OSF/Hugging Face "
                        "publication rules."
                    ),
                )
            )
    return rows


def write_research_linkages(
    rows: list[ResearchLinkageRecord],
    *,
    output_dir: Path,
) -> tuple[Path, Path]:
    """Write research linkage rows."""
    output_dir.mkdir(parents=True, exist_ok=True)
    data = [row.model_dump(mode="json") for row in rows]
    jsonl_path = write_jsonl(data, output_dir / "research_dataset_linkages.jsonl")
    csv_path = write_csv(data, output_dir / "research_dataset_linkages.csv")
    return jsonl_path, csv_path


def _group_by_track(
    records: Iterable[OutputArtifactPlanRecord],
) -> dict[str, list[OutputArtifactPlanRecord]]:
    grouped: dict[str, list[OutputArtifactPlanRecord]] = {}
    for record in records:
        grouped.setdefault(record.track_id, []).append(record)
    return grouped


def _mapping_resources_by_topic(
    records: Iterable[MappingResourceRecord],
) -> dict[str, list[MappingResourceRecord]]:
    grouped: dict[str, list[MappingResourceRecord]] = {
        "genomics": [],
        "medicine": [],
        "general": [],
    }
    for record in records:
        text = f"{record.domain} {record.name} {record.mapping_strategy}".lower()
        if any(token in text for token in ("genomic", "loinc", "hpo", "hgnc", "clingen")):
            grouped["genomics"].append(record)
        elif any(token in text for token in ("medicine", "drug", "rx", "atc")):
            grouped["medicine"].append(record)
        else:
            grouped["general"].append(record)
    return grouped


def _topic_for_question(question: ResearchQuestionRecord) -> str:
    text = f"{question.id} {question.question}".lower()
    if any(token in text for token in ("genomic", "pathology")):
        return "genomics"
    if any(token in text for token in ("medicine", "drug")):
        return "medicine"
    return "general"


def _row(
    question: ResearchQuestionRecord,
    linked_entity_type: Literal["source", "dataset_candidate", "mapping_resource", "output"],
    linked_entity_id: str,
    linked_entity_label: str,
    linkage_role: str,
    readiness_status: Literal["available", "planned", "blocked", "missing", "local_only"],
    recommended_action: str,
) -> ResearchLinkageRecord:
    return ResearchLinkageRecord(
        id=_slug(f"{question.id}_{linked_entity_type}_{linked_entity_id}"),
        research_question_id=question.id,
        track_id=question.track_id,
        linked_entity_type=linked_entity_type,
        linked_entity_id=linked_entity_id,
        linked_entity_label=linked_entity_label,
        linkage_role=linkage_role,
        readiness_status=readiness_status,
        recommended_action=recommended_action,
    )


def _slug(value: str) -> str:
    safe = "".join(character.lower() if character.isalnum() else "_" for character in value)
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_") or "linkage"

"""Evidence-readiness scoring for protocolled research questions."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Literal, cast

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import EvidenceReadinessRecord
from reimburse_atlas.registry import project_root, read_jsonl


def build_evidence_readiness(  # noqa: PLR0914
    root: Path | None = None,
) -> list[EvidenceReadinessRecord]:
    """Build research-question evidence-readiness rows from generated governance artefacts."""
    repo = root or project_root()
    questions = _read_rows(repo / "data" / "seed" / "research_questions.jsonl")
    protocol_rows = _read_rows(repo / "data" / "derived" / "protocols" / "protocol_status.jsonl")
    linkage_rows = _read_rows(
        repo / "data" / "derived" / "roadmap_linkages" / "research_dataset_linkages.jsonl"
    )
    data_quality_rows = _read_rows(
        repo / "data" / "derived" / "data_quality" / "data_quality_checks.jsonl"
    )
    source_validation_rows = _read_rows(
        repo / "data" / "derived" / "source_validation" / "source_content_validation.jsonl"
    )

    protocol_by_question = {str(row.get("research_question_id")): row for row in protocol_rows}
    linkages_by_question: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in linkage_rows:
        linkages_by_question[str(row.get("research_question_id"))].append(row)

    data_quality_blockers = sum(
        1
        for row in data_quality_rows
        if row.get("severity") == "blocking" and row.get("status") in {"fail", "missing"}
    )
    source_validation_blockers = sum(
        1 for row in source_validation_rows if row.get("validation_status") == "fail"
    )

    readiness: list[EvidenceReadinessRecord] = []
    for question in questions:
        question_id = str(question["id"])
        linkages = linkages_by_question.get(question_id, [])
        counts = Counter(
            cast(
                "Literal['available', 'planned', 'blocked', 'missing', 'local_only']",
                str(row.get("readiness_status", "missing")),
            )
            for row in linkages
        )
        entity_counts = Counter(
            cast(
                "Literal['source', 'dataset_candidate', 'mapping_resource', 'output']",
                str(row.get("linked_entity_type", "unknown")),
            )
            for row in linkages
        )
        protocol_score = float(
            protocol_by_question.get(question_id, {}).get("completeness_score", 0.0)
        )
        dataset_linkage_count = sum(
            1
            for row in linkages
            if row.get("linked_entity_type") in {"source", "dataset_candidate"}
        )
        output_plan_count = entity_counts.get("output", 0)
        mapping_resource_count = entity_counts.get("mapping_resource", 0)
        readiness_score = _readiness_score(
            protocol_score=protocol_score,
            counts=counts,
            dataset_linkage_count=dataset_linkage_count,
            output_plan_count=output_plan_count,
            mapping_resource_count=mapping_resource_count,
            data_quality_blockers=data_quality_blockers,
            source_validation_blockers=source_validation_blockers,
        )
        stage = _stage_from_score(
            readiness_score,
            protocol_score=protocol_score,
            data_quality_blockers=data_quality_blockers,
            source_validation_blockers=source_validation_blockers,
            missing_linkages=counts.get("missing", 0),
        )
        readiness.append(
            EvidenceReadinessRecord(
                id=f"evidence_readiness_{question_id}",
                research_question_id=question_id,
                track_id=str(question["track_id"]),
                protocol_score=round(protocol_score, 4),
                dataset_linkage_count=dataset_linkage_count,
                available_linkage_count=counts.get("available", 0),
                planned_linkage_count=counts.get("planned", 0),
                blocked_linkage_count=counts.get("blocked", 0),
                missing_linkage_count=counts.get("missing", 0),
                mapping_resource_count=mapping_resource_count,
                output_plan_count=output_plan_count,
                data_quality_blockers=data_quality_blockers,
                source_validation_blockers=source_validation_blockers,
                readiness_score=round(readiness_score, 4),
                readiness_stage=stage,
                recommended_action=_recommended_action(
                    stage,
                    protocol_score=protocol_score,
                    missing_linkages=counts.get("missing", 0),
                    blocked_linkages=counts.get("blocked", 0),
                    data_quality_blockers=data_quality_blockers,
                    source_validation_blockers=source_validation_blockers,
                ),
            )
        )
    return readiness


def write_evidence_readiness(
    rows: list[EvidenceReadinessRecord],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write evidence-readiness rows and a compact summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = [row.model_dump(mode="json") for row in rows]
    jsonl_path = write_jsonl(payload, output_dir / "evidence_readiness.jsonl")
    csv_path = write_csv(payload, output_dir / "evidence_readiness.csv")
    summary = {
        "research_question_count": len(rows),
        "evidence_ready": sum(row.readiness_stage == "evidence_ready" for row in rows),
        "prototype_ready": sum(row.readiness_stage == "prototype_ready" for row in rows),
        "design": sum(row.readiness_stage == "design" for row in rows),
        "blocked": sum(row.readiness_stage == "blocked" for row in rows),
        "average_readiness_score": round(sum(row.readiness_score for row in rows) / len(rows), 4)
        if rows
        else 0.0,
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return jsonl_path, csv_path, summary_path


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return read_jsonl(path)


def _readiness_score(
    *,
    protocol_score: float,
    counts: Counter[str],
    dataset_linkage_count: int,
    output_plan_count: int,
    mapping_resource_count: int,
    data_quality_blockers: int,
    source_validation_blockers: int,
) -> float:
    linkage_count = sum(counts.values())
    available_or_planned = counts.get("available", 0) + 0.55 * counts.get("planned", 0)
    linkage_score = available_or_planned / linkage_count if linkage_count else 0.0
    dataset_score = min(dataset_linkage_count / 4, 1.0)
    mapping_score = min(mapping_resource_count / 2, 1.0)
    output_score = min(output_plan_count / 2, 1.0)
    blocker_penalty = min(0.35, 0.08 * data_quality_blockers + 0.12 * source_validation_blockers)
    return max(
        0.0,
        min(
            1.0,
            0.32 * protocol_score
            + 0.28 * linkage_score
            + 0.18 * dataset_score
            + 0.12 * mapping_score
            + 0.10 * output_score
            - blocker_penalty,
        ),
    )


def _stage_from_score(
    score: float,
    *,
    protocol_score: float,
    data_quality_blockers: int,
    source_validation_blockers: int,
    missing_linkages: int,
) -> Literal["blocked", "design", "prototype_ready", "evidence_ready"]:
    if data_quality_blockers or source_validation_blockers:
        return "blocked"
    if score >= 0.86 and protocol_score >= 0.9 and missing_linkages == 0:
        return "evidence_ready"
    if score >= 0.62 and protocol_score >= 0.65:
        return "prototype_ready"
    return "design"


def _recommended_action(  # noqa: PLR0911
    stage: Literal["blocked", "design", "prototype_ready", "evidence_ready"],
    *,
    protocol_score: float,
    missing_linkages: int,
    blocked_linkages: int,
    data_quality_blockers: int,
    source_validation_blockers: int,
) -> str:
    if data_quality_blockers:
        return "Resolve blocking data-quality failures before interpreting results."
    if source_validation_blockers:
        return "Resolve failing source-content validation records before analysis."
    if protocol_score < 0.65:
        return "Expand the OSF protocol before source-specific analysis."
    if missing_linkages:
        return "Resolve missing research-question linkages or remove unsupported outputs."
    if blocked_linkages:
        return "Unblock gated datasets/mappings or document sensitivity exclusions."
    if stage == "evidence_ready":
        return "Ready for preregistered analysis once real reviewed-source bundles are present."
    if stage == "prototype_ready":
        return "Run the prototype analysis on reviewed derived data and add reviewer notes."
    return "Complete required dataset, mapping and output linkages."

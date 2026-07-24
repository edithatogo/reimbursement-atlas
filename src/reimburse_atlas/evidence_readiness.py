"""Evidence-readiness scoring for protocolled research questions."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Literal, cast

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import EvidenceReadinessRecord
from reimburse_atlas.registry import project_root, read_jsonl


def build_evidence_readiness(  # ruff:ignore[too-many-locals]
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
    claim_decisions = _read_rows(repo / "data" / "research_claims" / "decisions.jsonl")
    claims_by_question = {
        str(row.get("research_question_id")): _claim_package_state(repo, row)
        for row in claim_decisions
    }

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
        claim_status, claim_sha256, claim_review_record = claims_by_question.get(
            question_id, ("missing", None, None)
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
            claim_package_approved=claim_status == "approved",
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
                claim_package_status=claim_status,
                claim_package_sha256=claim_sha256,
                claim_review_record=claim_review_record,
                readiness_score=round(readiness_score, 4),
                readiness_stage=stage,
                recommended_action=_recommended_action(
                    stage,
                    protocol_score=protocol_score,
                    missing_linkages=counts.get("missing", 0),
                    blocked_linkages=counts.get("blocked", 0),
                    data_quality_blockers=data_quality_blockers,
                    source_validation_blockers=source_validation_blockers,
                    claim_package_status=claim_status,
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


def _claim_package_state(
    repo: Path, row: dict[str, Any]
) -> tuple[Literal["invalid", "pending", "approved"], str | None, str | None]:
    package_path = row.get("claim_package_path")
    expected_sha256 = row.get("claim_package_sha256")
    review_record = row.get("review_record")
    if not all(isinstance(value, str) and value for value in (package_path, expected_sha256)):
        return "invalid", None, str(review_record) if review_record else None
    candidate = (repo / str(package_path)).resolve()
    try:
        candidate.relative_to(repo.resolve())
    except ValueError:
        return "invalid", str(expected_sha256), str(review_record) if review_record else None
    if not candidate.is_file():
        return "invalid", str(expected_sha256), str(review_record) if review_record else None
    observed = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if observed != expected_sha256:
        return "invalid", str(expected_sha256), str(review_record) if review_record else None
    approved = (
        row.get("status") == "approved_within_scope"
        and row.get("reviewed_derived_inputs") is True
        and row.get("analysis_validated") is True
        and isinstance(review_record, str)
        and bool(review_record)
    )
    return (
        "approved" if approved else "pending",
        str(expected_sha256),
        str(review_record) if review_record else None,
    )


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
    claim_package_approved: bool,
    missing_linkages: int,
) -> Literal["blocked", "design", "prototype_ready", "evidence_ready"]:
    if data_quality_blockers or source_validation_blockers:
        return "blocked"
    if claim_package_approved and score >= 0.86 and protocol_score >= 0.9 and missing_linkages == 0:
        return "evidence_ready"
    if score >= 0.62 and protocol_score >= 0.65:
        return "prototype_ready"
    return "design"


def _recommended_action(  # ruff:ignore[too-many-return-statements]
    stage: Literal["blocked", "design", "prototype_ready", "evidence_ready"],
    *,
    protocol_score: float,
    missing_linkages: int,
    blocked_linkages: int,
    data_quality_blockers: int,
    source_validation_blockers: int,
    claim_package_status: Literal["missing", "invalid", "pending", "approved"],
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
    if claim_package_status == "invalid":
        return "Repair the missing or checksum-mismatched research claim package."
    if claim_package_status == "pending":
        return "Complete scoped accountable review of the checksum-bound claim package."
    if claim_package_status == "missing":
        return (
            "Run the analysis on reviewed derived data and create a checksum-bound claim package."
        )
    if stage == "evidence_ready":
        return "Ready for preregistered analysis once real reviewed-source bundles are present."
    if stage == "prototype_ready":
        return "Run the prototype analysis on reviewed derived data and add reviewer notes."
    return "Complete required dataset, mapping and output linkages."

"""Readiness calculations for sources and planned analyses."""

from __future__ import annotations

from dataclasses import asdict

from reimburse_atlas.models import AnalysisRecord, SourceRecord
from reimburse_atlas.scoring import GradeSensitivity, SourceScore, grade_sensitivity, score_sources


def source_readiness_rows(sources: list[SourceRecord]) -> list[dict[str, object]]:
    """Return flat source-readiness rows suitable for CSV or dashboard use."""
    scores = score_sources(sources)
    sources_by_id = {source.id: source for source in sources}
    rows: list[dict[str, object]] = []
    for score in scores:
        source = sources_by_id[score.source_id]
        rows.append({
            "source_id": source.id,
            "jurisdiction": source.jurisdiction,
            "system": source.system,
            "schedule": source.schedule,
            "domain": source.domain,
            "access_tier": source.access_tier,
            "score": score.score,
            "grade": score.grade,
            **{f"component_{key}": value for key, value in score.components.items()},
        })
    return rows


def _score_by_id(sources: list[SourceRecord]) -> dict[str, SourceScore]:
    return {score.source_id: score for score in score_sources(sources)}


def analysis_readiness_rows(
    analyses: list[AnalysisRecord],
    sources: list[SourceRecord],
) -> list[dict[str, object]]:
    """Score each planned analysis by the weakest required source."""
    score_map = _score_by_id(sources)
    rows: list[dict[str, object]] = []
    for analysis in analyses:
        required = list(analysis.required_sources)
        missing = [source_id for source_id in required if source_id not in score_map]
        available_scores = [
            score_map[source_id].score for source_id in required if source_id in score_map
        ]
        bottleneck = min(available_scores) if available_scores else 0
        mean_score = (
            round(sum(available_scores) / len(available_scores), 2) if available_scores else 0
        )
        rows.append({
            "analysis_id": analysis.id,
            "title": analysis.title,
            "difficulty": analysis.difficulty,
            "stage": analysis.stage,
            "required_source_count": len(required),
            "missing_source_count": len(missing),
            "missing_sources": ";".join(missing),
            "bottleneck_source_score": bottleneck,
            "mean_source_score": mean_score,
            "ready_for_prototype": not missing and bottleneck >= 8,
        })

    def sort_key(row: dict[str, object]) -> tuple[bool, float, str]:
        bottleneck = row["bottleneck_source_score"]
        numeric_bottleneck = float(bottleneck) if isinstance(bottleneck, (int, float)) else 0.0
        return (
            not bool(row["ready_for_prototype"]),
            -numeric_bottleneck,
            str(row["analysis_id"]),
        )

    return sorted(rows, key=sort_key)


def source_score_payload(score: SourceScore) -> dict[str, object]:
    """Serialise a source score without leaking dataclass internals to callers."""
    return asdict(score)


def readiness_grade_sensitivity_rows(
    sources: list[SourceRecord],
    threshold_sets: list[tuple[str, int, int, int]],
) -> list[dict[str, object]]:
    """Return deterministic grade-count sensitivity rows for source readiness.

    Threshold alternatives are reporting diagnostics only; the canonical
    :func:`reimburse_atlas.scoring.grade_for_score` thresholds remain unchanged.
    """
    scores = [score.score for score in score_sources(sources)]
    configurations = [(a_min, b_min, c_min) for _, a_min, b_min, c_min in threshold_sets]
    results = grade_sensitivity(scores, configurations)
    rows: list[dict[str, object]] = []
    for (label, _, _, _), result in zip(threshold_sets, results, strict=True):
        rows.append(_grade_sensitivity_row(label, result, len(scores)))
    return rows


def _grade_sensitivity_row(label: str, result: GradeSensitivity, total: int) -> dict[str, object]:
    """Flatten one sensitivity result for JSONL, CSV and dashboard consumers."""
    counts = result.counts
    return {
        "configuration": label,
        "a_min": result.a_min,
        "b_min": result.b_min,
        "c_min": result.c_min,
        "source_count": total,
        "grade_a_count": counts.get("A", 0),
        "grade_b_count": counts.get("B", 0),
        "grade_c_count": counts.get("C", 0),
        "grade_d_count": counts.get("D", 0),
        "prototype_ready_count": counts.get("A", 0) + counts.get("B", 0),
    }

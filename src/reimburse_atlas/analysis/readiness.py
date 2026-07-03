"""Readiness calculations for sources and planned analyses."""

from __future__ import annotations

from dataclasses import asdict

from reimburse_atlas.models import AnalysisRecord, SourceRecord
from reimburse_atlas.scoring import SourceScore, score_sources


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

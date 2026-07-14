"""Transparent source scoring helpers.

The score is deliberately simple and inspectable. It is not a judgement of a
health system; it is a research-readiness score for a public data source.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from reimburse_atlas.models import SourceRecord

Grade = Literal["A", "B", "C", "D"]


@dataclass(frozen=True)
class SourceScore:
    """Source readiness score with explanatory components."""

    source_id: str
    score: int
    grade: Grade
    components: dict[str, int]


@dataclass(frozen=True)
class GradeSensitivity:
    """Grade-count result for one alternative threshold configuration."""

    a_min: int
    b_min: int
    c_min: int
    counts: dict[Grade, int]


TIER_POINTS = {"tier_1": 4, "tier_2": 2, "tier_3": 0}
RELIABILITY_POINTS = {"high": 3, "medium": 1, "low": 0}


def grade_for_score(score: int) -> Grade:
    """Return a coarse grade for an access/readiness score."""
    if score >= 11:
        return "A"
    if score >= 8:
        return "B"
    if score >= 5:
        return "C"
    return "D"


def score_source(record: SourceRecord) -> SourceScore:
    """Score a source for reproducible comparative research."""
    components = {
        "access_tier": TIER_POINTS[record.access_tier],
        "machine_readable": 3 if record.machine_readable else 0,
        "historical_versions": 2 if record.historical_versions else 0,
        "utilisation_data": 2 if record.utilisation_data else 0,
        "reliability": RELIABILITY_POINTS[record.reliability],
    }
    score = sum(components.values())
    return SourceScore(record.id, score, grade_for_score(score), components)


def score_sources(records: list[SourceRecord]) -> list[SourceScore]:
    """Score sources and sort by grade, score and id."""
    return sorted(
        (score_source(record) for record in records),
        key=lambda item: (-item.score, item.source_id),
    )


def grade_sensitivity(
    scores: Iterable[int],
    threshold_sets: Iterable[tuple[int, int, int]],
) -> list[GradeSensitivity]:
    """Evaluate grade counts under alternative ``(A, B, C)`` cutoffs.

    The canonical :func:`grade_for_score` thresholds are not changed. This is
    an interpretation aid for robustness checks and reporting.
    """
    score_values = tuple(scores)
    results: list[GradeSensitivity] = []
    for a_min, b_min, c_min in threshold_sets:
        if not (a_min > b_min > c_min >= 0):
            msg = "thresholds must satisfy A > B > C >= 0"
            raise ValueError(msg)
        counts: dict[Grade, int] = {"A": 0, "B": 0, "C": 0, "D": 0}
        for score in score_values:
            grade: Grade
            if score >= a_min:
                grade = "A"
            elif score >= b_min:
                grade = "B"
            elif score >= c_min:
                grade = "C"
            else:
                grade = "D"
            counts[grade] += 1
        results.append(GradeSensitivity(a_min, b_min, c_min, counts))
    return results

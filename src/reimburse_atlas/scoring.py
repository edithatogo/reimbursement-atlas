"""Transparent source scoring helpers.

The score is deliberately simple and inspectable. It is not a judgement of a
health system; it is a research-readiness score for a public data source.
"""

from __future__ import annotations

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

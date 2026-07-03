"""Quality gates for source and analysis registries."""

from __future__ import annotations

from collections import Counter

from reimburse_atlas.models import AnalysisRecord, SourceRecord, SourceVersionRecord


def duplicate_source_ids(records: list[SourceRecord]) -> list[str]:
    """Return duplicated source ids."""
    counts = Counter(record.id for record in records)
    return sorted(source_id for source_id, count in counts.items() if count > 1)


def missing_analysis_sources(
    analyses: list[AnalysisRecord],
    valid_source_ids: set[str],
) -> dict[str, tuple[str, ...]]:
    """Find analysis records referencing sources absent from the registry."""
    missing: dict[str, tuple[str, ...]] = {}
    for analysis in analyses:
        absent = tuple(sorted(set(analysis.required_sources) - valid_source_ids))
        if absent:
            missing[analysis.id] = absent
    return missing


def access_tier_counts(records: list[SourceRecord]) -> dict[str, int]:
    """Count source records by access tier."""
    counts = Counter(record.access_tier for record in records)
    return dict(sorted(counts.items()))


def missing_source_version_sources(
    versions: list[SourceVersionRecord],
    valid_source_ids: set[str],
) -> dict[str, str]:
    """Find source-version records referencing absent source ids."""
    return {
        version.id: version.source_id
        for version in versions
        if version.source_id not in valid_source_ids
    }

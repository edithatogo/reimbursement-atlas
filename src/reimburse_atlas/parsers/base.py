"""Parser protocols for source-specific ingestion."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from reimburse_atlas.contracts import CoverageDecisionRecord, ScheduleItemRecord


class ScheduleItemParser(Protocol):
    """Protocol for parsers that emit normalised schedule items."""

    def __call__(self, path: Path) -> list[ScheduleItemRecord]:
        """Parse a source file into schedule item records."""
        ...


class CoverageDecisionParser(Protocol):
    """Protocol for parsers that emit normalised coverage decisions."""

    def __call__(self, path: Path) -> list[CoverageDecisionRecord]:
        """Parse a source file into coverage decision records."""
        ...

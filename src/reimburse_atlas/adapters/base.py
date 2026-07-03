"""Source adapter interfaces for reimbursement schedule ingestion.

Adapters convert source-specific public files into conservative internal records.
They intentionally avoid network access by default: acquisition and parsing are
separate so every live download can pass a licence/provenance gate first.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pydantic import HttpUrl

from reimburse_atlas.contracts import CoverageDecisionRecord, ScheduleItemRecord
from reimburse_atlas.models import FrozenModel, NonEmptyStr, SourceId


class AdapterError(RuntimeError):
    """Raised when an adapter cannot parse a source file."""


class SourceAcquisitionPlan(FrozenModel):
    """A planned source acquisition that has not necessarily been fetched."""

    source_id: SourceId
    version_id: SourceId
    url: HttpUrl
    expected_format: NonEmptyStr
    parser_name: NonEmptyStr
    acquisition_mode: NonEmptyStr
    licence_gate: NonEmptyStr
    cache_policy: NonEmptyStr
    notes: NonEmptyStr


@dataclass(frozen=True)
class ParsedPayload:
    """A parser result containing normalised schedule and decision records."""

    schedule_items: tuple[ScheduleItemRecord, ...] = ()
    coverage_decisions: tuple[CoverageDecisionRecord, ...] = ()

    def __bool__(self) -> bool:
        """Return true when any records were parsed."""
        return bool(self.schedule_items or self.coverage_decisions)


class SourceAdapter(Protocol):
    """Protocol implemented by all source adapters."""

    source_id: str
    name: str
    supported_formats: Sequence[str]

    def parse_file(self, path: Path) -> ParsedPayload:
        """Parse a local file into normalised records."""
        ...


def require_file(path: Path) -> None:
    """Raise a consistent error when an expected local fixture is missing."""
    if not path.exists():
        msg = f"Input file does not exist: {path}"
        raise AdapterError(msg)
    if not path.is_file():
        msg = f"Input path is not a file: {path}"
        raise AdapterError(msg)


def non_empty_rows(rows: Iterable[dict[str, str]], path: Path) -> list[dict[str, str]]:
    """Return non-empty CSV rows or raise a useful adapter error."""
    materialised = [row for row in rows if any(value.strip() for value in row.values())]
    if not materialised:
        msg = f"No usable rows parsed from {path}"
        raise AdapterError(msg)
    return materialised

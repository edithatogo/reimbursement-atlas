"""Fixture parser for early schedule-item contract development."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.contracts import ScheduleItemRecord


def _read_json_or_jsonl(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [
            cast("dict[str, Any]", json.loads(line)) for line in text.splitlines() if line.strip()
        ]
    loaded = json.loads(text)
    if not isinstance(loaded, list):
        msg = f"Expected a JSON array in {path}"
        raise TypeError(msg)
    return cast("list[dict[str, Any]]", loaded)


def parse_schedule_item_fixture(path: Path) -> list[ScheduleItemRecord]:
    """Parse a permissive fixture into schedule item contracts."""
    return [ScheduleItemRecord.model_validate(row) for row in _read_json_or_jsonl(path)]

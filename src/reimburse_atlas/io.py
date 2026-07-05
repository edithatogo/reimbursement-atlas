"""Small file IO helpers for generated atlas artefacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def write_jsonl(rows: list[dict[str, Any]], path: Path) -> Path:
    """Write rows as deterministic newline-delimited JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    return path


def write_csv(rows: list[dict[str, Any]], path: Path) -> Path:
    """Write rows to CSV, creating a header from all observed keys."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({field for row in rows for field in row}) if rows else ["empty"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(_csv_safe_row(row) for row in rows)
    return path


def pydantic_rows(records: list[Any]) -> list[dict[str, Any]]:
    """Serialise Pydantic records to JSON-compatible dictionaries."""
    return [record.model_dump(mode="json") for record in records]


def _csv_safe_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert nested/list values into deterministic JSON strings for CSV."""
    safe: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, (list, tuple, dict)):
            safe[key] = json.dumps(value, sort_keys=True, default=str)
        else:
            safe[key] = value
    return safe

"""Repository-local validation utilities for generated seed artefacts."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root


@dataclass(frozen=True)
class SeedFilePairStatus:
    """Consistency status for a JSONL/CSV seed table pair."""

    table_name: str
    jsonl_path: str
    csv_path: str
    jsonl_rows: int
    csv_rows: int
    jsonl_ids: int
    csv_ids: int
    missing_in_csv: tuple[str, ...]
    missing_in_jsonl: tuple[str, ...]
    ok: bool

    def as_row(self) -> dict[str, Any]:
        """Return a serialisable row for JSONL/CSV outputs."""
        row = asdict(self)
        row["missing_in_csv"] = list(self.missing_in_csv)
        row["missing_in_jsonl"] = list(self.missing_in_jsonl)
        return row


def read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL table into dictionaries."""
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        loaded = json.loads(line)
        if not isinstance(loaded, dict):
            msg = f"{path}:{line_number} is not a JSON object"
            raise TypeError(msg)
        rows.append(cast("dict[str, Any]", loaded))
    return rows


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV table into dictionaries."""
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _ids(rows: list[dict[str, Any]]) -> set[str]:
    return {str(row["id"]) for row in rows if row.get("id") not in (None, "")}


def compare_seed_pair(table_name: str, seed_dir: Path | None = None) -> SeedFilePairStatus:
    """Compare the row/id status of one JSONL/CSV seed pair."""
    base = seed_dir or project_root() / "data" / "seed"
    jsonl_path = base / f"{table_name}.jsonl"
    csv_path = base / f"{table_name}.csv"
    jsonl_rows = read_jsonl_rows(jsonl_path)
    csv_rows = read_csv_rows(csv_path)
    jsonl_ids = _ids(jsonl_rows)
    csv_ids = _ids(csv_rows)
    missing_in_csv = tuple(sorted(jsonl_ids - csv_ids))
    missing_in_jsonl = tuple(sorted(csv_ids - jsonl_ids))
    ok = (
        jsonl_path.exists()
        and csv_path.exists()
        and len(jsonl_rows) == len(csv_rows)
        and not missing_in_csv
        and not missing_in_jsonl
    )
    return SeedFilePairStatus(
        table_name=table_name,
        jsonl_path=str(jsonl_path),
        csv_path=str(csv_path),
        jsonl_rows=len(jsonl_rows),
        csv_rows=len(csv_rows),
        jsonl_ids=len(jsonl_ids),
        csv_ids=len(csv_ids),
        missing_in_csv=missing_in_csv,
        missing_in_jsonl=missing_in_jsonl,
        ok=ok,
    )


DEFAULT_SEED_PAIRS = (
    "source_registry",
    "source_versions",
    "source_files",
    "source_status",
    "source_snapshots",
    "analysis_catalogue",
    "ontology_registry",
    "analysis_recipes",
    "ontology_concepts",
    "ontology_mapping_templates",
)


def seed_pair_statuses(
    seed_dir: Path | None = None,
    table_names: tuple[str, ...] = DEFAULT_SEED_PAIRS,
) -> list[SeedFilePairStatus]:
    """Return consistency statuses for the core seed tables that have CSV mirrors."""
    base = seed_dir or project_root() / "data" / "seed"
    return [
        compare_seed_pair(table_name, base)
        for table_name in table_names
        if (base / f"{table_name}.jsonl").exists() or (base / f"{table_name}.csv").exists()
    ]


def all_seed_pairs_ok(statuses: list[SeedFilePairStatus]) -> bool:
    """Return true when all inspected seed pairs are synchronised."""
    return all(status.ok for status in statuses)

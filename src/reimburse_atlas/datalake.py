"""Local seed-lake materialisation helpers."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root


@dataclass(frozen=True)
class SeedLakeTable:
    """A materialised seed-lake table."""

    name: str
    rows: int
    jsonl_path: str
    csv_path: str
    sha256: str


@dataclass(frozen=True)
class SeedLakeManifest:
    """Manifest for generated local seed-lake artifacts."""

    table_count: int
    tables: tuple[SeedLakeTable, ...]
    duckdb_path: str | None = None
    parquet_enabled: bool = False


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            loaded = json.loads(line)
            if isinstance(loaded, dict):
                rows.append(cast("dict[str, Any]", loaded))
    return rows


def _write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, default=str) + "\n")


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    fields = sorted({field for row in rows for field in row}) if rows else ["empty"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(_csv_safe_row(row) for row in rows)


def _csv_safe_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert nested/list values into deterministic JSON strings for CSV."""
    safe: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, (list, tuple, dict)):
            safe[key] = json.dumps(value, sort_keys=True, default=str)
        else:
            safe[key] = value
    return safe


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def materialise_seed_lake(output_dir: Path | None = None) -> SeedLakeManifest:
    """Materialise seed registries into JSONL/CSV and optional analytical formats."""
    root = project_root()
    base = output_dir or root / "data" / "derived" / "seed_lake"
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True, exist_ok=True)

    seed_dir = root / "data" / "seed"
    source_tables = {
        "source_registry": _read_jsonl(seed_dir / "source_registry.jsonl"),
        "analysis_catalogue": _read_jsonl(seed_dir / "analysis_catalogue.jsonl"),
        "ontology_registry": _read_jsonl(seed_dir / "ontology_registry.jsonl"),
        "source_versions": _read_jsonl(seed_dir / "source_versions.jsonl"),
        "source_files": _read_jsonl(seed_dir / "source_files.jsonl"),
        "source_snapshots": _read_jsonl(seed_dir / "source_snapshots.jsonl"),
        "source_status": _read_jsonl(seed_dir / "source_status.jsonl"),
        "sample_schedule_items": _read_jsonl(seed_dir / "sample_schedule_items.jsonl"),
        "analysis_recipes": _read_jsonl(seed_dir / "analysis_recipes.jsonl")
        if (seed_dir / "analysis_recipes.jsonl").exists()
        else [],
        "ontology_concepts": _read_jsonl(seed_dir / "ontology_concepts.jsonl")
        if (seed_dir / "ontology_concepts.jsonl").exists()
        else [],
        "ontology_mapping_templates": _read_jsonl(seed_dir / "ontology_mapping_templates.jsonl")
        if (seed_dir / "ontology_mapping_templates.jsonl").exists()
        else [],
    }
    vertical_dir = root / "data" / "derived" / "vertical_slice"
    for table_name in (
        "schedule_items",
        "coverage_decisions",
        "crosswalk_candidates",
        "crosswalk_review_queue",
        "median_payment_by_source",
        "priced_share",
        "policy_signal_matrix",
    ):
        table_path = vertical_dir / f"{table_name}.jsonl"
        if table_path.exists():
            source_tables[f"vertical_{table_name}"] = _read_jsonl(table_path)

    tables: list[SeedLakeTable] = []
    for name, rows in source_tables.items():
        table_dir = base / name
        table_dir.mkdir(parents=True, exist_ok=True)
        jsonl_path = table_dir / f"{name}.jsonl"
        csv_path = table_dir / f"{name}.csv"
        _write_jsonl(rows, jsonl_path)
        _write_csv(rows, csv_path)
        tables.append(
            SeedLakeTable(
                name=name,
                rows=len(rows),
                jsonl_path=str(jsonl_path.relative_to(base)),
                csv_path=str(csv_path.relative_to(base)),
                sha256=_sha256(jsonl_path),
            )
        )

    manifest = SeedLakeManifest(table_count=len(tables), tables=tuple(tables))
    manifest_path = base / "manifest.json"
    manifest_path.write_text(json.dumps(asdict(manifest), indent=2, sort_keys=True) + "\n")
    return manifest

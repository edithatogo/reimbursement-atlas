"""Generate a dashboard-safe data dictionary for seed and derived public artefacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import DataDictionaryRecord
from reimburse_atlas.publication import (
    DEFAULT_PUBLICATION_PATHS,
    count_rows,
    reviewed_source_bundle_paths,
)
from reimburse_atlas.registry import project_root


def build_data_dictionary(root: Path | None = None) -> list[DataDictionaryRecord]:
    """Build data dictionary rows for all existing publication-manifest candidate paths."""
    repo = root or project_root()
    rows: list[DataDictionaryRecord] = []
    candidate_paths = tuple(
        dict.fromkeys((*DEFAULT_PUBLICATION_PATHS, *reviewed_source_bundle_paths(repo)))
    )
    for relative_path in candidate_paths:
        path = repo / relative_path
        if not path.exists() or _is_raw_or_local_path(relative_path):
            continue
        columns = _columns_for(path)
        scope, gate, notes = _scope_gate_notes(relative_path)
        rows.append(
            DataDictionaryRecord(
                id=_safe_id(f"data_dictionary_{relative_path.with_suffix('')!s}"),
                table_name=relative_path.stem,
                relative_path=str(relative_path),
                file_format=relative_path.suffix.lstrip(".") or "unknown",
                row_count=count_rows(path),
                column_count=len(columns),
                columns=tuple(columns),
                publication_scope=scope,
                licence_gate=gate,
                notes=notes,
            )
        )
    return rows


def write_data_dictionary(
    rows: list[DataDictionaryRecord],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write data dictionary rows and summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = [row.model_dump(mode="json") for row in rows]
    jsonl_path = write_jsonl(payload, output_dir / "data_dictionary.jsonl")
    csv_path = write_csv(payload, output_dir / "data_dictionary.csv")
    summary = {
        "table_count": len(rows),
        "total_rows_documented": sum(row.row_count for row in rows),
        "jsonl_tables": sum(row.file_format == "jsonl" for row in rows),
        "csv_tables": sum(row.file_format == "csv" for row in rows),
        "json_tables": sum(row.file_format in {"json", "jsonld"} for row in rows),
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return jsonl_path, csv_path, summary_path


def _columns_for(path: Path) -> list[str]:
    if path.suffix == ".jsonl":
        columns: set[str] = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            loaded = json.loads(line)
            if isinstance(loaded, dict):
                loaded_dict = cast("dict[str, Any]", loaded)
                columns.update(str(key) for key in loaded_dict)
        return sorted(columns)
    if path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or [])
    loaded = _read_json(path)
    if isinstance(loaded, dict):
        loaded_dict = cast("dict[str, Any]", loaded)
        return sorted(str(key) for key in loaded_dict)
    return []


def _read_json(path: Path) -> Any:
    if path.suffix not in {".json", ".jsonld"}:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _scope_gate_notes(path: Path) -> tuple[str, str, str]:
    if "derived" in path.parts:
        return (
            "public_derived_candidate",
            "public_reuse_review",
            "Derived artefact; confirm source-specific licence gates before external release.",
        )
    return (
        "public_metadata_candidate",
        "public_reuse_review",
        "Seed metadata artefact; safe for review but still needs source licence notes checked.",
    )


def _is_raw_or_local_path(path: Path) -> bool:
    return bool({"raw", "raw_live", "local", "cache"} & set(path.parts))


def _safe_id(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_")

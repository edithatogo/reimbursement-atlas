"""Optional Arrow/LanceDB vector-index helpers for mapping workbench data."""

from __future__ import annotations

import importlib
from contextlib import suppress
from pathlib import Path
from typing import Any

from reimburse_atlas.analysis.mapping_evidence import hash_text_vector
from reimburse_atlas.contracts import ScheduleItemRecord


class VectorIndexDependencyError(RuntimeError):
    """Raised when Arrow or LanceDB dependencies are unavailable."""


def schedule_item_vector_rows(
    records: list[ScheduleItemRecord],
    *,
    dimensions: int = 48,
) -> list[dict[str, object]]:
    """Return deterministic vector rows for schedule-item search prototypes."""
    rows: list[dict[str, object]] = []
    for record in records:
        text = " ".join(
            part
            for part in (
                record.item_label,
                record.item_description,
                record.restriction_text,
                record.domain,
            )
            if part
        )
        rows.append({
            "source_id": record.source_id,
            "item_code": record.item_code,
            "item_label": record.item_label,
            "domain": record.domain,
            "vector": list(hash_text_vector(text, dimensions=dimensions)),
        })
    return rows


def write_arrow_vector_seed(rows: list[dict[str, object]], path: Path) -> Path:
    """Write vector rows to an Arrow IPC file when PyArrow is installed."""
    try:
        pa = importlib.import_module("pyarrow")
        ipc = importlib.import_module("pyarrow.ipc")
    except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
        msg = "pyarrow is required to write vector Arrow IPC files"
        raise VectorIndexDependencyError(msg) from exc

    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows)
    new_file = ipc.new_file
    with path.open("wb") as handle, new_file(handle, table.schema) as writer:
        writer.write_table(table)
    return path


def build_lancedb_index(
    rows: list[dict[str, object]],
    *,
    database_dir: Path,
    table_name: str = "schedule_item_vectors",
) -> Path:
    """Create or replace a small local LanceDB table for vector-search experiments."""
    try:
        lancedb = importlib.import_module("lancedb")
    except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
        msg = "lancedb is required to build the local vector index"
        raise VectorIndexDependencyError(msg) from exc

    database_dir.mkdir(parents=True, exist_ok=True)
    connect = lancedb.connect
    db = connect(str(database_dir))
    _create_or_replace_table(db, table_name, rows)
    return database_dir


def _create_or_replace_table(db: Any, table_name: str, rows: list[dict[str, object]]) -> None:
    with suppress(FileNotFoundError, ValueError, RuntimeError):
        db.drop_table(table_name)
    db.create_table(table_name, data=rows)

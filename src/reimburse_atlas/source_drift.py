"""Schema and row-count drift helpers for source and derived tabular artefacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import SourceDriftRecord
from reimburse_atlas.registry import project_root

DEFAULT_DRIFT_PAIRS: tuple[tuple[str, str, Path, Path], ...] = (
    (
        "source_registry_jsonl",
        "source_registry_csv",
        Path("data/seed/source_registry.jsonl"),
        Path("data/seed/source_registry.csv"),
    ),
    (
        "dataset_candidates_jsonl",
        "dataset_candidates_csv",
        Path("data/seed/dataset_candidates.jsonl"),
        Path("data/seed/dataset_candidates.csv"),
    ),
    (
        "research_questions_jsonl",
        "research_questions_csv",
        Path("data/seed/research_questions.jsonl"),
        Path("data/seed/research_questions.csv"),
    ),
    (
        "roadmap_functions_jsonl",
        "roadmap_functions_csv",
        Path("data/seed/roadmap_functions.jsonl"),
        Path("data/seed/roadmap_functions.csv"),
    ),
    (
        "source_validation_jsonl",
        "source_validation_csv",
        Path("data/derived/source_validation/source_content_validation.jsonl"),
        Path("data/derived/source_validation/source_content_validation.csv"),
    ),
    (
        "data_quality_jsonl",
        "data_quality_csv",
        Path("data/derived/data_quality/data_quality_checks.jsonl"),
        Path("data/derived/data_quality/data_quality_checks.csv"),
    ),
)


def compare_tabular_files(  # noqa: PLR0914
    left_path: Path,
    right_path: Path,
    *,
    left_label: str | None = None,
    right_label: str | None = None,
    root: Path | None = None,
) -> SourceDriftRecord:
    """Compare row counts, columns and checksums for two CSV/JSONL artefacts."""
    repo = root or project_root()
    left = left_path if left_path.is_absolute() else repo / left_path
    right = right_path if right_path.is_absolute() else repo / right_path
    left_name = left_label or left_path.stem
    right_name = right_label or right_path.stem
    record_id = _safe_id(f"source_drift_{left_name}_to_{right_name}")
    if not left.exists() or not right.exists():
        missing = [str(path) for path in (left, right) if not path.exists()]
        return SourceDriftRecord(
            id=record_id,
            left_label=left_name,
            right_label=right_name,
            left_path=_rel(left, repo),
            right_path=_rel(right, repo),
            status="missing",
            recommended_action=f"Generate missing artefact(s): {', '.join(missing)}.",
        )

    left_info = _tabular_info(left)
    right_info = _tabular_info(right)
    left_columns = set(left_info["columns"])
    right_columns = set(right_info["columns"])
    added_columns = tuple(sorted(right_columns - left_columns))
    removed_columns = tuple(sorted(left_columns - right_columns))
    left_count = int(left_info["row_count"])
    right_count = int(right_info["row_count"])
    delta = right_count - left_count
    delta_pct = round((delta / left_count) if left_count else 0.0, 6)
    status = _status_for_drift(
        left_count=left_count,
        right_count=right_count,
        added_columns=added_columns,
        removed_columns=removed_columns,
    )
    return SourceDriftRecord(
        id=record_id,
        left_label=left_name,
        right_label=right_name,
        left_path=_rel(left, repo),
        right_path=_rel(right, repo),
        status=status,
        left_row_count=left_count,
        right_row_count=right_count,
        row_count_delta=delta,
        row_count_delta_pct=delta_pct,
        added_columns=added_columns,
        removed_columns=removed_columns,
        left_checksum_sha256=_sha256(left),
        right_checksum_sha256=_sha256(right),
        recommended_action=_recommended_action(status, added_columns, removed_columns, delta),
    )


def build_default_source_drift_report(root: Path | None = None) -> list[SourceDriftRecord]:
    """Build default JSONL/CSV mirror and generated-artefact drift checks."""
    repo = root or project_root()
    return [
        compare_tabular_files(
            left, right, left_label=left_label, right_label=right_label, root=repo
        )
        for left_label, right_label, left, right in DEFAULT_DRIFT_PAIRS
    ]


def write_source_drift_report(
    rows: list[SourceDriftRecord],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write source-drift rows and summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = [row.model_dump(mode="json") for row in rows]
    jsonl_path = write_jsonl(payload, output_dir / "source_drift_report.jsonl")
    csv_path = write_csv(payload, output_dir / "source_drift_report.csv")
    summary = {
        "drift_check_count": len(rows),
        "pass": sum(row.status == "pass" for row in rows),
        "warn": sum(row.status == "warn" for row in rows),
        "fail": sum(row.status == "fail" for row in rows),
        "missing": sum(row.status == "missing" for row in rows),
        "blocking_failure_count": sum(row.status in {"fail", "missing"} for row in rows),
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return jsonl_path, csv_path, summary_path


def _tabular_info(path: Path) -> dict[str, Any]:
    if path.suffix == ".jsonl":
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
        columns = sorted({column for row in rows if isinstance(row, dict) for column in row})
        return {"row_count": len(rows), "columns": columns}
    if path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            columns = list(reader.fieldnames or [])
            row_count = sum(1 for _ in reader)
        return {"row_count": row_count, "columns": columns}
    text = path.read_text(encoding="utf-8")
    return {"row_count": len([line for line in text.splitlines() if line.strip()]), "columns": []}


def _status_for_drift(
    *,
    left_count: int,
    right_count: int,
    added_columns: tuple[str, ...],
    removed_columns: tuple[str, ...],
) -> str:
    if removed_columns:
        return "fail"
    if left_count != right_count:
        return "warn"
    if added_columns:
        return "warn"
    return "pass"


def _recommended_action(
    status: str,
    added_columns: tuple[str, ...],
    removed_columns: tuple[str, ...],
    row_delta: int,
) -> str:
    if status == "pass":
        return "No schema or row-count drift detected."
    if removed_columns:
        return "Review removed columns before release; this may be a breaking schema change."
    if row_delta:
        return "Review row-count drift and confirm it is expected for this release."
    if added_columns:
        return "Document added columns in the data dictionary and dashboard table configuration."
    return "Review drift record before release."


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_id(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_")


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)

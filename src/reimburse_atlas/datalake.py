"""Local seed-lake materialisation helpers."""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
import re
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
    parquet_path: str | None = None


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


def _optional_import_available(name: str) -> bool:
    try:
        __import__(name)
    except ModuleNotFoundError:
        return False
    return True


def _write_optional_parquet(rows: list[dict[str, Any]], path: Path) -> Path | None:
    if not _optional_import_available("pyarrow"):
        return None
    pa = importlib.import_module("pyarrow")
    pq = importlib.import_module("pyarrow.parquet")

    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist([_csv_safe_row(row) for row in rows] or [{"empty": ""}])
    write_table = pq.write_table
    write_table(table, path)
    return path


def _write_optional_duckdb(
    tables: list[SeedLakeTable],
    *,
    base: Path,
    database_path: Path,
) -> None:
    duckdb = importlib.import_module("duckdb")

    if database_path.exists():
        database_path.unlink()
    con = duckdb.connect(str(database_path))
    try:
        for table in tables:
            table_name = _safe_table_name(table.name)
            csv_path = base / table.csv_path
            con.execute(
                f"create or replace table {table_name} as select * from read_csv_auto(?)",  # nosec B608
                [str(csv_path)],
            )
    finally:
        con.close()


def _safe_table_name(name: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) is None:
        msg = f"Unsafe table name: {name}"
        raise ValueError(msg)
    return name


def materialise_seed_lake(output_dir: Path | None = None) -> SeedLakeManifest:  # noqa: PLR0914
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
        "conductor_tracks": _read_jsonl(seed_dir / "conductor_tracks.jsonl")
        if (seed_dir / "conductor_tracks.jsonl").exists()
        else [],
        "roadmap_functions": _read_jsonl(seed_dir / "roadmap_functions.jsonl")
        if (seed_dir / "roadmap_functions.jsonl").exists()
        else [],
        "dataset_candidates": _read_jsonl(seed_dir / "dataset_candidates.jsonl")
        if (seed_dir / "dataset_candidates.jsonl").exists()
        else [],
        "mapping_resources": _read_jsonl(seed_dir / "mapping_resources.jsonl")
        if (seed_dir / "mapping_resources.jsonl").exists()
        else [],
        "research_questions": _read_jsonl(seed_dir / "research_questions.jsonl")
        if (seed_dir / "research_questions.jsonl").exists()
        else [],
        "output_artifact_plans": _read_jsonl(seed_dir / "output_artifact_plans.jsonl")
        if (seed_dir / "output_artifact_plans.jsonl").exists()
        else [],
        "runtime_targets": _read_jsonl(seed_dir / "runtime_targets.jsonl")
        if (seed_dir / "runtime_targets.jsonl").exists()
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
        "mapping_evidence_matrix",
    ):
        table_path = vertical_dir / f"{table_name}.jsonl"
        if table_path.exists():
            source_tables[f"vertical_{table_name}"] = _read_jsonl(table_path)

    derived_jsonl_tables = {
        "repo_workflow_uses": root / "data" / "derived" / "repo_automation" / "workflow_uses.jsonl",
        "repo_workflow_policy": root
        / "data"
        / "derived"
        / "repo_automation"
        / "workflow_policy.jsonl",
        "repo_automation_controls": root
        / "data"
        / "derived"
        / "repo_automation"
        / "automation_controls.jsonl",
        "repo_action_sha_pin_plan": root
        / "data"
        / "derived"
        / "repo_automation"
        / "action_sha_pin_plan.jsonl",
        "repo_action_pin_resolution": root
        / "data"
        / "derived"
        / "repo_automation"
        / "action_pin_resolution.jsonl",
        "sbom_summary": root / "data" / "derived" / "sbom" / "sbom_summary.jsonl",
        "local_quality_gates": root
        / "data"
        / "derived"
        / "local_quality_gates"
        / "local_quality_gates.jsonl",
        "local_quality_gate_specs": root
        / "data"
        / "derived"
        / "local_quality_gates"
        / "local_quality_gate_specs.jsonl",
        "architecture_import_edges": root
        / "data"
        / "derived"
        / "architecture"
        / "import_edges.jsonl",
        "architecture_layer_policy": root
        / "data"
        / "derived"
        / "architecture"
        / "layer_policy.jsonl",
        "architecture_import_cycles": root
        / "data"
        / "derived"
        / "architecture"
        / "import_cycles.jsonl",
        "release_readiness_gates": root
        / "data"
        / "derived"
        / "release_readiness"
        / "release_gates.jsonl",
        "source_download_plans": root
        / "data"
        / "derived"
        / "source_downloads"
        / "download_plans.jsonl",
        "source_download_attempts": root
        / "data"
        / "derived"
        / "source_downloads"
        / "download_attempts.jsonl",
        "source_content_validation": root
        / "data"
        / "derived"
        / "source_validation"
        / "source_content_validation.jsonl",
        "osf_component_plan": root / "data" / "derived" / "osf" / "component_plan.jsonl",
        "protocol_status": root / "data" / "derived" / "protocols" / "protocol_status.jsonl",
        "research_dataset_linkages": root
        / "data"
        / "derived"
        / "roadmap_linkages"
        / "research_dataset_linkages.jsonl",
        "data_quality_checks": root
        / "data"
        / "derived"
        / "data_quality"
        / "data_quality_checks.jsonl",
    }
    for table_name, table_path in derived_jsonl_tables.items():
        if table_path.exists():
            source_tables[table_name] = _read_jsonl(table_path)

    parquet_available = _optional_import_available("pyarrow")
    duckdb_available = _optional_import_available("duckdb")
    duckdb_path = base / "seed_lake.duckdb"

    tables: list[SeedLakeTable] = []
    for name, rows in source_tables.items():
        table_dir = base / name
        table_dir.mkdir(parents=True, exist_ok=True)
        jsonl_path = table_dir / f"{name}.jsonl"
        csv_path = table_dir / f"{name}.csv"
        _write_jsonl(rows, jsonl_path)
        _write_csv(rows, csv_path)
        parquet_path = _write_optional_parquet(rows, table_dir / f"{name}.parquet")
        tables.append(
            SeedLakeTable(
                name=name,
                rows=len(rows),
                jsonl_path=str(jsonl_path.relative_to(base)),
                csv_path=str(csv_path.relative_to(base)),
                sha256=_sha256(jsonl_path),
                parquet_path=(
                    str(parquet_path.relative_to(base)) if parquet_path is not None else None
                ),
            )
        )

    if duckdb_available:
        _write_optional_duckdb(tables, base=base, database_path=duckdb_path)

    manifest = SeedLakeManifest(
        table_count=len(tables),
        tables=tuple(tables),
        duckdb_path=str(duckdb_path.relative_to(base)) if duckdb_available else None,
        parquet_enabled=parquet_available,
    )
    manifest_path = base / "manifest.json"
    manifest_path.write_text(json.dumps(asdict(manifest), indent=2, sort_keys=True) + "\n")
    return manifest

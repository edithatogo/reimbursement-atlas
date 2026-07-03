"""Generate first-wave ingestion-plan seed files."""

from __future__ import annotations

from reimburse_atlas.ingest import build_first_wave_ingestion_plan, write_ingestion_plan
from reimburse_atlas.registry import load_source_registry, load_source_versions, project_root


def main() -> None:
    """Write first-wave ingestion-plan JSONL and CSV files."""
    tasks = build_first_wave_ingestion_plan(load_source_registry(), load_source_versions())
    jsonl_path, csv_path = write_ingestion_plan(tasks, project_root() / "data" / "seed")
    print(f"Wrote {len(tasks)} ingestion tasks to {jsonl_path} and {csv_path}")


if __name__ == "__main__":
    main()

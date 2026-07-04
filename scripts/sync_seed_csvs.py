"""Synchronise CSV mirrors from JSONL seed tables."""

from __future__ import annotations

from reimburse_atlas.io import write_csv
from reimburse_atlas.registry import project_root, read_jsonl

TABLES = (
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


def main() -> None:
    """Regenerate CSV mirrors for seed JSONL tables that exist."""
    seed_dir = project_root() / "data" / "seed"
    written = 0
    for table in TABLES:
        jsonl_path = seed_dir / f"{table}.jsonl"
        if not jsonl_path.exists():
            continue
        rows = read_jsonl(jsonl_path)
        write_csv(rows, seed_dir / f"{table}.csv")
        written += 1
    print(f"Synchronised {written} seed CSV mirrors")


if __name__ == "__main__":
    main()

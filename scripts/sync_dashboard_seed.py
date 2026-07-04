"""Copy approved seed/derived CSV assets into the Astro dashboard public directory."""

from __future__ import annotations

import shutil
from pathlib import Path

from reimburse_atlas.registry import project_root

FILES = [
    Path("data/seed/graph_nodes.csv"),
    Path("data/seed/graph_edges.csv"),
    Path("data/seed/source_readiness.csv"),
    Path("data/seed/analysis_readiness.csv"),
    Path("data/seed/first_wave_ingestion_plan.csv"),
    Path("data/seed/source_acquisition_plan.csv"),
    Path("data/seed/source_files.csv"),
    Path("data/seed/ingestion_readiness.csv"),
    Path("data/seed/source_snapshots.csv"),
    Path("data/seed/source_status.csv"),
    Path("data/seed/analysis_recipes.csv"),
    Path("data/seed/ontology_registry.csv"),
    Path("data/seed/ontology_concepts.csv"),
    Path("data/seed/ontology_mapping_templates.csv"),
    Path("data/derived/vertical_slice/schedule_items.csv"),
    Path("data/derived/vertical_slice/coverage_decisions.csv"),
    Path("data/derived/vertical_slice/crosswalk_candidates.csv"),
    Path("data/derived/vertical_slice/crosswalk_review_queue.csv"),
    Path("data/derived/vertical_slice/median_payment_by_source.csv"),
    Path("data/derived/vertical_slice/priced_share.csv"),
    Path("data/derived/vertical_slice/policy_signal_matrix.csv"),
    Path("data/derived/external_quality_gates.csv"),
]


def main() -> None:
    """Synchronise dashboard-safe generated CSV files."""
    root = project_root()
    output_dir = root / "apps" / "dashboard" / "public" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for relative_path in FILES:
        source = root / relative_path
        if not source.exists():
            continue
        target = output_dir / source.name
        shutil.copy2(source, target)
        copied += 1
    print(f"Copied {copied} dashboard seed files to {output_dir}")


if __name__ == "__main__":
    main()

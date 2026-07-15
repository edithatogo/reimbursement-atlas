"""Smoke tests for dashboard reproducibility and dashboard-safe seed assets."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = ROOT / "apps" / "dashboard"
DATA = DASHBOARD / "public" / "data"

REQUIRED_DASHBOARD_FILES = (
    DASHBOARD / "package.json",
    DASHBOARD / "package-lock.json",
    DASHBOARD / "astro.config.mjs",
    DASHBOARD / "src" / "components" / "DataTable.astro",
    DASHBOARD / "src" / "components" / "Graph.tsx",
)

REQUIRED_DASHBOARD_DATA = (
    "graph_nodes.csv",
    "graph_edges.csv",
    "source_status.csv",
    "source_files.csv",
    "source_readiness.csv",
    "source_acquisition_plan.csv",
    "source_snapshots.csv",
    "analysis_recipes.csv",
    "policy_signal_matrix.csv",
    "crosswalk_review_queue.csv",
    "ontology_registry.csv",
    "ontology_concepts.csv",
    "ontology_mapping_templates.csv",
    "external_quality_gates.csv",
    "licence_review_queue.csv",
)


def test_dashboard_lockfile_and_entrypoints_exist() -> None:
    """The dashboard should be reproducible from a committed npm lockfile."""
    missing = [path for path in REQUIRED_DASHBOARD_FILES if not path.exists()]
    assert missing == []


def test_dashboard_safe_csv_assets_are_synced() -> None:
    """Pages should not point to generated CSV files missing from public/data."""
    missing = [name for name in REQUIRED_DASHBOARD_DATA if not (DATA / name).exists()]
    assert missing == []

"""Generate minimal CycloneDX SBOMs for Python and dashboard dependencies."""

from __future__ import annotations

import json
from typing import Any, cast

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.registry import project_root
from reimburse_atlas.sbom import build_dashboard_sbom, build_python_sbom, sbom_summary, write_sbom


def main() -> None:
    """Write SBOM JSON files and dashboard-safe summary rows."""
    root = project_root()
    out_dir = root / "data" / "derived" / "sbom"
    python_bom = build_python_sbom(root)
    dashboard_bom = build_dashboard_sbom(root)
    write_sbom(python_bom, out_dir / "cyclonedx-python.json")
    write_sbom(dashboard_bom, out_dir / "cyclonedx-dashboard.json")
    rows = [sbom_summary(python_bom), sbom_summary(dashboard_bom)]
    write_jsonl(rows, out_dir / "sbom_summary.jsonl")
    write_csv(rows, out_dir / "sbom_summary.csv")
    component_count = sum(int(cast("dict[str, Any]", row)["component_count"]) for row in rows)
    print(json.dumps({"sboms": len(rows), "components": component_count}, indent=2))


if __name__ == "__main__":
    main()

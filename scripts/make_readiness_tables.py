"""Generate source and analysis readiness tables."""

from __future__ import annotations

from reimburse_atlas.analysis import analysis_readiness_rows, source_readiness_rows
from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.registry import load_analysis_catalogue, load_source_registry, project_root


def main() -> None:
    """Write readiness CSV/JSONL files for dashboard and review."""
    out = project_root() / "data" / "seed"
    sources = load_source_registry()
    analyses = load_analysis_catalogue()
    source_rows = source_readiness_rows(sources)
    analysis_rows = analysis_readiness_rows(analyses, sources)
    write_jsonl(source_rows, out / "source_readiness.jsonl")
    write_csv(source_rows, out / "source_readiness.csv")
    write_jsonl(analysis_rows, out / "analysis_readiness.jsonl")
    write_csv(analysis_rows, out / "analysis_readiness.csv")
    print(f"Wrote {len(source_rows)} source rows and {len(analysis_rows)} analysis rows")


if __name__ == "__main__":
    main()

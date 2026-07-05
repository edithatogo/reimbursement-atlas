"""Generate research-question linkage rows for datasets, mappings and outputs."""

from __future__ import annotations

from reimburse_atlas.registry import (
    load_dataset_candidates,
    load_mapping_resources,
    load_output_artifact_plans,
    load_research_questions,
    load_source_registry,
    project_root,
)
from reimburse_atlas.roadmap_linkages import build_research_linkages, write_research_linkages


def main() -> None:
    """Write research linkage artefacts."""
    rows = build_research_linkages(
        research_questions=load_research_questions(),
        sources=load_source_registry(),
        dataset_candidates=load_dataset_candidates(),
        mapping_resources=load_mapping_resources(),
        output_plans=load_output_artifact_plans(),
    )
    paths = write_research_linkages(
        rows,
        output_dir=project_root() / "data" / "derived" / "roadmap_linkages",
    )
    print(f"Wrote {len(rows)} research linkage rows: {', '.join(str(path) for path in paths)}")


if __name__ == "__main__":
    main()

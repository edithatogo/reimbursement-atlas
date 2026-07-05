"""Generate OSF component and publication-plan artefacts."""

from __future__ import annotations

from reimburse_atlas.osf import build_osf_component_plan, write_osf_outputs
from reimburse_atlas.registry import (
    load_output_artifact_plans,
    load_research_questions,
    project_root,
)


def main() -> None:
    """Write OSF plan artefacts."""
    components = build_osf_component_plan(load_research_questions(), load_output_artifact_plans())
    paths = write_osf_outputs(components, output_dir=project_root() / "data" / "derived" / "osf")
    print({"component_count": len(components), "paths": [str(path) for path in paths]})


if __name__ == "__main__":
    main()

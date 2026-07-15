"""Generate OSF component and publication-plan artefacts."""

from __future__ import annotations

from reimburse_atlas.osf import build_osf_component_plan, write_osf_outputs
from reimburse_atlas.osf_registration import build_registration_freeze, write_registration_freeze
from reimburse_atlas.registry import (
    load_output_artifact_plans,
    load_research_questions,
    project_root,
    repo_relative,
)


def main() -> None:
    """Write OSF plan artefacts."""
    components = build_osf_component_plan(load_research_questions(), load_output_artifact_plans())
    paths = write_osf_outputs(components, output_dir=project_root() / "data" / "derived" / "osf")
    freeze = build_registration_freeze(
        root=project_root(),
        sync_manifest_path=project_root() / "data" / "derived" / "osf" / "sync_manifest.jsonl",
    )
    freeze_path = write_registration_freeze(
        freeze, project_root() / "data" / "derived" / "osf" / "registration_freeze.json"
    )
    paths = (*paths, freeze_path)
    print({"component_count": len(components), "paths": [repo_relative(path) for path in paths]})


if __name__ == "__main__":
    main()

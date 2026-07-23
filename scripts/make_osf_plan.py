"""Generate OSF component and publication-plan artefacts."""

from __future__ import annotations

import json

from reimburse_atlas.io import write_jsonl
from reimburse_atlas.osf import build_osf_component_plan, write_osf_outputs
from reimburse_atlas.osf_registration import (
    apply_publication_decision,
    apply_registration_decision,
    build_registration_freeze,
    build_registration_review_packet,
    read_optional_object,
    write_registration_freeze,
    write_registration_review_packet,
)
from reimburse_atlas.registry import (
    load_output_artifact_plans,
    load_research_questions,
    project_root,
    repo_relative,
)


def main() -> None:
    """Write OSF plan artefacts."""
    components = build_osf_component_plan(load_research_questions(), load_output_artifact_plans())
    root = project_root()
    output_dir = root / "data" / "derived" / "osf"
    paths = write_osf_outputs(components, output_dir=output_dir)
    sync_manifest_path = output_dir / "sync_manifest.jsonl"
    manifest_rows = [
        json.loads(line)
        for line in sync_manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    publication_decision = read_optional_object(
        root / "data" / "osf_review" / "publication_decision.json"
    )
    write_jsonl(
        apply_publication_decision(manifest_rows, publication_decision),
        sync_manifest_path,
    )
    freeze = build_registration_freeze(
        root=root,
        sync_manifest_path=sync_manifest_path,
    )
    freeze = apply_registration_decision(
        freeze,
        read_optional_object(root / "data" / "osf_review" / "registration_decision.json"),
    )
    freeze_path = write_registration_freeze(freeze, output_dir / "registration_freeze.json")
    review_packet = build_registration_review_packet(
        freeze_path=freeze_path,
        protocol_status_path=project_root()
        / "data"
        / "derived"
        / "protocols"
        / "protocol_status.jsonl",
        sync_manifest_path=sync_manifest_path,
    )
    review_packet_path = write_registration_review_packet(
        review_packet,
        project_root() / "data" / "derived" / "osf" / "registration_review_packet.md",
    )
    paths = (*paths, freeze_path, review_packet_path)
    print({"component_count": len(components), "paths": [repo_relative(path) for path in paths]})


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.models import SourceFileRecord
from reimburse_atlas.osf import build_osf_component_plan, write_osf_outputs
from reimburse_atlas.registry import (
    load_conductor_tracks,
    load_dataset_candidates,
    load_mapping_resources,
    load_output_artifact_plans,
    load_research_questions,
    load_roadmap_functions,
    load_runtime_targets,
)
from reimburse_atlas.research_package import (
    build_dcat,
    build_frictionless_package,
    build_ro_crate,
    write_research_package,
)
from reimburse_atlas.source_downloads import (
    attempt_download,
    build_download_plan,
    safe_local_target,
    write_download_outputs,
)


def test_v14_seed_tables_are_loadable() -> None:
    assert load_conductor_tracks()
    assert load_roadmap_functions()
    assert load_dataset_candidates()
    assert load_mapping_resources()
    assert load_research_questions()
    assert load_output_artifact_plans()
    runtime_targets = {target.id: target for target in load_runtime_targets()}
    assert runtime_targets["rt_mojo"].name == "Mojo"
    assert "3.14" in runtime_targets["rt_python314"].version_target


def _source_file(**overrides: object) -> SourceFileRecord:
    payload: dict[str, object] = {
        "id": "test_file",
        "source_id": "au_mbs",
        "source_version_id": "au_mbs_seed_fixture",
        "file_label": "Test file",
        "file_name": "Unsafe API/CSV file name.txt",
        "source_url": "https://example.org/test.txt",
        "file_role": "primary",
        "expected_format": "text/plain",
        "acquisition_mode": "manual_download",
        "licence_gate": "permissive_candidate",
        "parser_hint": "fixture",
        "expected_record_count": 1,
        "current_observation": "fixture",
        "notes": "fixture",
    }
    payload.update(overrides)
    return SourceFileRecord.model_validate(payload)


def test_download_plan_sanitises_target_and_respects_licence_gate(tmp_path: Path) -> None:
    record = _source_file()
    target = safe_local_target(record, tmp_path)
    assert target.name == "Unsafe_API_CSV_file_name.txt"
    plan = build_download_plan(record, output_dir=tmp_path)
    assert plan.should_execute
    assert "curl" in plan.command

    gated = _source_file(id="gated", file_role="licence_gate", licence_gate="metadata_only")
    gated_plan = build_download_plan(gated, output_dir=tmp_path)
    assert not gated_plan.should_execute


def test_attempt_download_skips_metadata_only(tmp_path: Path) -> None:
    gated = _source_file(id="gated", file_role="licence_gate", licence_gate="metadata_only")
    attempt = attempt_download(gated, output_dir=tmp_path)
    assert attempt.status == "skipped_licence_gate"
    assert attempt.bytes_downloaded == 0
    assert attempt.exit_code is None


def test_write_download_outputs(tmp_path: Path) -> None:
    record = _source_file()
    plan = build_download_plan(record, output_dir=tmp_path / "raw")
    attempt = attempt_download(
        _source_file(id="gated", file_role="landing_page", licence_gate="metadata_only"),
        output_dir=tmp_path / "raw",
    )
    paths = write_download_outputs([plan], [attempt], output_dir=tmp_path / "out")
    assert all(path.exists() for path in paths)
    assert (tmp_path / "out" / "download_commands.sh").exists()


def test_osf_component_plan_and_outputs(tmp_path: Path) -> None:
    questions = load_research_questions()
    outputs = load_output_artifact_plans()
    components = build_osf_component_plan(questions, outputs)
    assert any(component.component_type == "protocol" for component in components)
    assert any(component.component_type == "report" for component in components)
    paths = write_osf_outputs(components, output_dir=tmp_path)
    assert all(path.exists() for path in paths)
    manifest = json.loads((tmp_path / "osf_publication_manifest.json").read_text())
    assert manifest["component_count"] == len(components)
    assert "raw restricted" in manifest["raw_data_policy"]
    checklist = (tmp_path / "preprint_checklist.md").read_text()
    assert checklist.startswith("# OSF preprint checklist")
    assert "Protocol components" in checklist
    assert "Source-content validation" in checklist
    assert "genomics_pathology_protocol.md" in checklist


def test_osf_sync_manifest_is_checksum_bearing_and_fail_closed(tmp_path: Path) -> None:
    components = build_osf_component_plan(load_research_questions(), load_output_artifact_plans())
    paths = write_osf_outputs(
        components,
        output_dir=tmp_path / "data/derived/osf",
        root=Path(__file__).parents[2],
    )
    sync_rows = [json.loads(line) for line in paths[3].read_text(encoding="utf-8").splitlines()]
    assert sync_rows
    assert all(row["publish_allowed"] is False for row in sync_rows)
    assert all("blocked_reason" in row for row in sync_rows)


def test_osf_sync_manifest_hashes_large_files_incrementally(tmp_path: Path) -> None:
    from reimburse_atlas.osf import OsfComponentPlan, sha256_file

    payload = (b"reimbursement-atlas\n" * 100_000) + b"end\n"
    source = tmp_path / "large.txt"
    source.write_bytes(payload)
    component = OsfComponentPlan(
        id="large",
        component_title="Large",
        component_type="file",
        local_path="large.txt",
        osf_path="/large.txt",
        required_before_release=False,
        research_question_id=None,
        notes="fixture",
    )
    paths = write_osf_outputs([component], output_dir=tmp_path / "out", root=tmp_path)
    row = json.loads(paths[3].read_text(encoding="utf-8").strip())
    assert row["byte_size"] == len(payload)
    assert row["sha256"] == sha256_file(source)


def test_research_package_metadata(tmp_path: Path) -> None:
    paths = write_research_package(tmp_path)
    assert all(path.exists() for path in paths)
    datapackage = json.loads((tmp_path / "datapackage.json").read_text())
    crate = json.loads((tmp_path / "ro-crate-metadata.json").read_text())
    dcat = json.loads((tmp_path / "dcat.jsonld").read_text())
    assert datapackage["profile"] == "data-package"
    assert datapackage["resources"]
    assert crate["@context"] == "https://w3id.org/ro/crate/1.2/context"
    assert dcat["@type"] == "dcat:Dataset"


def test_research_package_builders_accept_manifest() -> None:
    from reimburse_atlas.publication import build_publication_manifest

    manifest = build_publication_manifest()
    assert build_frictionless_package(manifest)["resources"]
    assert build_ro_crate(manifest)["@graph"]
    assert build_dcat(manifest)["dcat:distribution"]


def test_research_package_generation_is_deterministic(tmp_path: Path) -> None:
    """Descriptor hashes must not refer to the previous descriptor generation."""
    paths = write_research_package(tmp_path)
    first = [path.read_bytes() for path in paths]
    write_research_package(tmp_path)
    assert [path.read_bytes() for path in paths] == first


def test_research_package_descriptors_exclude_themselves(tmp_path: Path) -> None:
    """Descriptors must not list or hash any descriptor from their own output set."""
    paths = write_research_package(tmp_path)
    descriptor_names = {path.name for path in paths}
    datapackage = json.loads((tmp_path / "datapackage.json").read_text(encoding="utf-8"))
    crate = json.loads((tmp_path / "ro-crate-metadata.json").read_text(encoding="utf-8"))
    dcat = json.loads((tmp_path / "dcat.jsonld").read_text(encoding="utf-8"))

    resource_paths = {str(resource["path"]) for resource in datapackage["resources"]}
    crate_ids = {str(node.get("@id")) for node in crate["@graph"]}
    distribution_paths = {
        str(distribution["dcat:downloadURL"]) for distribution in dcat["dcat:distribution"]
    }

    assert descriptor_names.isdisjoint(resource_paths)
    assert (descriptor_names - {"ro-crate-metadata.json"}).isdisjoint(crate_ids)
    assert descriptor_names.isdisjoint(distribution_paths)

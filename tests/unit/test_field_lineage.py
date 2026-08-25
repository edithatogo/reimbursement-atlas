"""Field-level lineage and standards projection tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from reimburse_atlas.field_lineage import (
    FieldLineageRecord,
    build_identity_field_lineage,
    build_openlineage_events,
    build_prov_o,
    build_ro_crate_lineage,
    write_field_lineage_outputs,
)


def _records() -> tuple[FieldLineageRecord, ...]:
    return build_identity_field_lineage(
        source_dataset="data/seed/source_registry.jsonl",
        output_dataset="data/seed/source_registry.csv",
        fields=("jurisdiction", "id"),
        transformation_id="sync_seed_csvs:source_registry_jsonl_to_csv:v1",
        code_version=f"sha256:{'c' * 64}",
        input_sha256="a" * 64,
        output_sha256="b" * 64,
        rights_decision_id="source_registry_metadata_scope",
    )


def test_field_records_bind_required_reproducibility_identity() -> None:
    records = _records()
    assert [row.output_field for row in records] == ["id", "jurisdiction"]
    assert all(row.source_field == row.output_field for row in records)
    assert all(row.input_sha256 == "a" * 64 for row in records)
    assert all(row.output_sha256 == "b" * 64 for row in records)
    assert len({row.record_id for row in records}) == 2


def test_field_lineage_rejects_unsafe_or_self_referential_edges() -> None:
    payload = _records()[0].model_dump()
    payload["source_dataset"] = "/unsafe/source.jsonl"
    with pytest.raises(ValidationError, match="repository-relative"):
        FieldLineageRecord.model_validate(payload)
    payload = _records()[0].model_dump()
    payload["output_dataset"] = payload["source_dataset"]
    payload["output_field"] = payload["source_field"]
    with pytest.raises(ValidationError, match="identify a transformation"):
        FieldLineageRecord.model_validate(payload)


def test_prov_o_projection_links_entities_activity_and_fixity() -> None:
    graph = build_prov_o(_records())["@graph"]
    assert any(node.get("@type") == "prov:Activity" for node in graph)
    outputs = [node for node in graph if "prov:wasDerivedFrom" in node]
    assert len(outputs) == 2
    assert all(node["reimburse:sha256"] == "b" * 64 for node in outputs)
    assert all("prov:wasGeneratedBy" in node for node in outputs)


def test_ro_crate_projection_uses_create_actions_and_derivation() -> None:
    crate = build_ro_crate_lineage(_records())
    actions = [node for node in crate["@graph"] if node.get("@type") == "CreateAction"]
    assert len(actions) == 2
    assert all("prov:wasDerivedFrom" in node for node in actions)


def test_openlineage_projection_has_column_lineage_facet() -> None:
    event = build_openlineage_events(_records())[0]
    fields = event["outputs"][0]["facets"]["columnLineage"]["fields"]
    assert sorted(fields) == ["id", "jurisdiction"]
    assert fields["id"]["inputFields"][0]["field"] == "id"
    assert event["run"]["runId"] == "b" * 64


def test_output_generation_is_deterministic(tmp_path: Path) -> None:
    paths = write_field_lineage_outputs(_records(), tmp_path)
    first = [path.read_bytes() for path in paths]
    write_field_lineage_outputs(_records(), tmp_path)
    assert [path.read_bytes() for path in paths] == first
    native = [json.loads(line) for line in paths[0].read_text().splitlines()]
    assert len(native) == 2

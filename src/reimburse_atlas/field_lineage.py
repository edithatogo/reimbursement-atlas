"""Checksum-bound field lineage and standards projections."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Annotated, Any

from pydantic import Field, model_validator

from reimburse_atlas.models import FrozenModel, NonEmptyStr

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class FieldLineageRecord(FrozenModel):
    """One source-field to output-field transformation edge."""

    record_id: Sha256
    source_dataset: NonEmptyStr
    source_field: NonEmptyStr
    transformation_id: NonEmptyStr
    output_dataset: NonEmptyStr
    output_field: NonEmptyStr
    code_version: NonEmptyStr
    input_sha256: Sha256
    output_sha256: Sha256
    rights_decision_id: NonEmptyStr

    @model_validator(mode="after")
    def require_distinct_safe_datasets(self) -> FieldLineageRecord:
        """Reject unsafe paths and self-referential transformation edges."""
        for value in (self.source_dataset, self.output_dataset):
            path = value.replace("\\", "/")
            if path.startswith("/") or ".." in path.split("/"):
                message = "lineage datasets must be repository-relative"
                raise ValueError(message)
        if self.source_dataset == self.output_dataset and self.source_field == self.output_field:
            message = "lineage edge must identify a transformation"
            raise ValueError(message)
        return self


def sha256_file(path: Path) -> str:
    """Return a streaming SHA-256 digest."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _record_id(payload: dict[str, str]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def build_identity_field_lineage(
    *,
    source_dataset: str,
    output_dataset: str,
    fields: tuple[str, ...],
    transformation_id: str,
    code_version: str,
    input_sha256: str,
    output_sha256: str,
    rights_decision_id: str,
) -> tuple[FieldLineageRecord, ...]:
    """Build deterministic identity-field edges for a format transformation."""
    records: list[FieldLineageRecord] = []
    for field in sorted(fields):
        identity = {
            "source_dataset": source_dataset,
            "source_field": field,
            "transformation_id": transformation_id,
            "output_dataset": output_dataset,
            "output_field": field,
            "code_version": code_version,
            "input_sha256": input_sha256,
            "output_sha256": output_sha256,
            "rights_decision_id": rights_decision_id,
        }
        records.append(FieldLineageRecord(record_id=_record_id(identity), **identity))
    return tuple(records)


def build_prov_o(records: tuple[FieldLineageRecord, ...]) -> dict[str, Any]:
    """Project field lineage as a deterministic PROV-O JSON-LD graph."""
    graph: list[dict[str, Any]] = []
    activities: set[str] = set()
    for row in records:
        activity_id = f"urn:reimburse-atlas:transformation:{row.transformation_id}"
        source_id = f"urn:reimburse-atlas:field:{row.input_sha256}:{row.source_field}"
        output_id = f"urn:reimburse-atlas:field:{row.output_sha256}:{row.output_field}"
        if activity_id not in activities:
            activities.add(activity_id)
            graph.append({
                "@id": activity_id,
                "@type": "prov:Activity",
                "prov:value": row.code_version,
            })
        graph.extend([
            {
                "@id": source_id,
                "@type": "prov:Entity",
                "prov:atLocation": row.source_dataset,
                "prov:value": row.source_field,
                "reimburse:sha256": row.input_sha256,
            },
            {
                "@id": output_id,
                "@type": "prov:Entity",
                "prov:atLocation": row.output_dataset,
                "prov:value": row.output_field,
                "prov:wasDerivedFrom": {"@id": source_id},
                "prov:wasGeneratedBy": {"@id": activity_id},
                "reimburse:sha256": row.output_sha256,
                "reimburse:rightsDecision": row.rights_decision_id,
            },
        ])
    return {
        "@context": {
            "prov": "http://www.w3.org/ns/prov#",
            "reimburse": "https://edithatogo.github.io/reimbursement-atlas/ns#",
        },
        "@graph": graph,
    }


def build_ro_crate_lineage(records: tuple[FieldLineageRecord, ...]) -> dict[str, Any]:
    """Project field edges into an RO-Crate 1.2 metadata graph."""
    graph: list[dict[str, Any]] = [
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "about": {"@id": "./"},
            "conformsTo": {"@id": "https://w3id.org/ro/crate/1.2"},
        },
        {
            "@id": "./",
            "@type": "Dataset",
            "name": "Reimbursement Atlas field lineage",
            "hasPart": [{"@id": f"#lineage-{row.record_id}"} for row in records],
        },
    ]
    graph.extend(
        {
            "@id": f"#lineage-{row.record_id}",
            "@type": "CreateAction",
            "name": row.transformation_id,
            "instrument": row.code_version,
            "object": {"@id": f"{row.source_dataset}#{row.source_field}"},
            "result": {"@id": f"{row.output_dataset}#{row.output_field}"},
            "prov:wasDerivedFrom": {"@id": f"{row.source_dataset}#{row.source_field}"},
        }
        for row in records
    )
    return {
        "@context": [
            "https://w3id.org/ro/crate/1.2/context",
            {"prov": "http://www.w3.org/ns/prov#"},
        ],
        "@graph": graph,
    }


def build_openlineage_events(
    records: tuple[FieldLineageRecord, ...],
) -> tuple[dict[str, Any], ...]:
    """Project records into deterministic OpenLineage COMPLETE events."""
    grouped: dict[tuple[str, str, str, str, str], list[FieldLineageRecord]] = {}
    for row in records:
        key = (
            row.transformation_id,
            row.code_version,
            row.source_dataset,
            row.output_dataset,
            row.output_sha256,
        )
        grouped.setdefault(key, []).append(row)
    events: list[dict[str, Any]] = []
    for key, rows in sorted(grouped.items()):
        transformation_id, code_version, source_dataset, output_dataset, output_sha = key
        events.append({
            "eventType": "COMPLETE",
            "eventTime": "1970-01-01T00:00:00Z",
            "producer": "https://github.com/edithatogo/reimbursement-atlas",
            "schemaURL": "https://openlineage.io/spec/2-0-2/OpenLineage.json",
            "run": {"runId": output_sha},
            "job": {
                "namespace": "reimbursement-atlas",
                "name": transformation_id,
                "facets": {
                    "codeVersion": {
                        "_producer": "reimbursement-atlas",
                        "version": code_version,
                    }
                },
            },
            "inputs": [{"namespace": "reimbursement-atlas", "name": source_dataset}],
            "outputs": [
                {
                    "namespace": "reimbursement-atlas",
                    "name": output_dataset,
                    "facets": {
                        "columnLineage": {
                            "_producer": "reimbursement-atlas",
                            "_schemaURL": "https://openlineage.io/spec/facets/1-2-0/ColumnLineageDatasetFacet.json",
                            "fields": {
                                row.output_field: {
                                    "inputFields": [
                                        {
                                            "namespace": "reimbursement-atlas",
                                            "name": source_dataset,
                                            "field": row.source_field,
                                        }
                                    ]
                                }
                                for row in sorted(rows, key=lambda item: item.output_field)
                            },
                        }
                    },
                }
            ],
        })
    return tuple(events)


def write_field_lineage_outputs(
    records: tuple[FieldLineageRecord, ...], output_dir: Path
) -> tuple[Path, Path, Path, Path]:
    """Write native, PROV-O, RO-Crate, and OpenLineage representations."""
    output_dir.mkdir(parents=True, exist_ok=True)
    native = output_dir / "field_lineage.jsonl"
    prov = output_dir / "field_lineage.prov.jsonld"
    crate = output_dir / "field_lineage.ro-crate.jsonld"
    openlineage = output_dir / "field_lineage.openlineage.jsonl"
    native.write_text(
        "".join(json.dumps(row.model_dump(mode="json"), sort_keys=True) + "\n" for row in records),
        encoding="utf-8",
    )
    prov.write_text(json.dumps(build_prov_o(records), indent=2, sort_keys=True) + "\n")
    crate.write_text(json.dumps(build_ro_crate_lineage(records), indent=2, sort_keys=True) + "\n")
    openlineage.write_text(
        "".join(
            json.dumps(event, sort_keys=True) + "\n" for event in build_openlineage_events(records)
        ),
        encoding="utf-8",
    )
    return native, prov, crate, openlineage

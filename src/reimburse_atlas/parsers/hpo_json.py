"""Human Phenotype Ontology OBO Graph JSON parser."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord

HPO_URL: HttpUrl = cast("HttpUrl", "https://purl.obolibrary.org/obo/hp.json")


def parse_hpo_json(
    path: Path,
    *,
    source_version: str = "hpo_current_20260723",
    retrieved_at: str | None = None,
) -> list[ScheduleItemRecord]:
    """Parse active HPO classes into provenance-bound terminology records."""
    payload = cast("dict[str, Any]", json.loads(path.read_text(encoding="utf-8")))
    graphs = cast("list[dict[str, Any]]", payload.get("graphs", []))
    nodes = cast("list[dict[str, Any]]", graphs[0].get("nodes", [])) if graphs else []
    records: list[ScheduleItemRecord] = []
    for node in nodes:
        identifier = str(node.get("id", ""))
        label = str(node.get("lbl", "")).strip()
        meta = cast("dict[str, Any]", node.get("meta", {}))
        if (
            not identifier.endswith(tuple(f"HP_{digit}" for digit in range(10)))
            and "HP_" not in identifier
        ):
            continue
        if not label or meta.get("deprecated") is True:
            continue
        code = identifier.rsplit("/", maxsplit=1)[-1].replace("_", ":", 1)
        definition = cast("dict[str, Any]", meta.get("definition", {})).get("val")
        records.append(
            ScheduleItemRecord(
                source_id="hpo",
                jurisdiction="International",
                domain="genomics",
                code_system="HPO",
                item_code=code,
                item_label=label,
                item_description=str(definition).strip() if definition else None,
                payment_unit="terminology_concept",
                provenance=ProvenanceRecord(
                    source_id="hpo",
                    source_url=HPO_URL,
                    retrieved_at=retrieved_at,
                    source_version=source_version,
                    licence_class="permissive",
                    transformation_notes=(
                        "Parsed active HPO class identifier, label and definition from the CC0 "
                        "OBO Graph JSON distribution."
                    ),
                ),
            )
        )
    return records

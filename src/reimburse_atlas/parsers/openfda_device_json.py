"""openFDA device product-classification parser."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord

OPENFDA_URL: HttpUrl = cast("HttpUrl", "https://api.fda.gov/device/classification.json?limit=1000")


def parse_openfda_device_classification(
    path: Path,
    *,
    source_version: str = "us_fda_device_classification_20260723_page1",
    retrieved_at: str | None = None,
) -> list[ScheduleItemRecord]:
    """Parse public generic FDA device classification fields."""
    payload = cast("dict[str, Any]", json.loads(path.read_text(encoding="utf-8")))
    results = cast("list[dict[str, Any]]", payload.get("results", []))
    records: list[ScheduleItemRecord] = []
    for row in results:
        code = str(row.get("product_code", "")).strip()
        name = str(row.get("device_name", "")).strip()
        if not code or not name:
            continue
        device_class = str(row.get("device_class", "")).strip()
        specialty = str(row.get("medical_specialty_description", "")).strip()
        regulation = str(row.get("regulation_number", "")).strip()
        records.append(
            ScheduleItemRecord(
                source_id="us_fda_device_classification",
                jurisdiction="United States",
                domain="devices",
                code_system="FDA_PRODUCT_CODE",
                item_code=code,
                item_label=name,
                item_description=str(row.get("definition", "")).strip() or None,
                payment_unit="device_classification",
                restriction_text=(
                    f"device_class={device_class};regulation={regulation}".rstrip(";")
                ),
                setting=specialty or None,
                provenance=ProvenanceRecord(
                    source_id="us_fda_device_classification",
                    source_url=OPENFDA_URL,
                    retrieved_at=retrieved_at,
                    source_version=source_version,
                    licence_class="public_reuse_unclear",
                    transformation_notes=(
                        "Parsed public openFDA generic classification fields. This is not "
                        "clinical advice, a reimbursement price, or a complete device corpus."
                    ),
                ),
            )
        )
    return records

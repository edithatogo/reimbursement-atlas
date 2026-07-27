"""Parser for the public PHARMAC Pharmaceutical Schedule XML."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, cast

from defusedxml import ElementTree as ET
from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord

SOURCE_URL = cast(
    "HttpUrl",
    "https://schedule.pharmac.govt.nz/pub/schedule/archive/Schedule_2026-07.xml",
)
NS = {"s": "http://schedule.pharmac.govt.nz/2006/07/Schedule#"}


def parse_pharmac_xml(path: Path) -> list[ScheduleItemRecord]:
    """Return one bounded public-price row per PHARMAC pack."""
    root = ET.parse(path).getroot()
    if root is None:
        msg = "PHARMAC XML has no document root"
        raise ValueError(msg)
    records: list[ScheduleItemRecord] = []
    for chemical in root.findall(".//s:Chemical", NS):
        chemical_name = _text(chemical.find("s:Name", NS))
        for formulation in chemical.findall("s:Formulation", NS):
            formulation_name = _text(formulation.find("s:Name", NS))
            for brand in formulation.findall("s:Brand", NS):
                brand_name = _text(brand.find("s:Name", NS))
                for pack in brand.findall("s:Pack", NS):
                    pack_id = pack.attrib.get("ID", "").strip()
                    if not pack_id or not chemical_name:
                        continue
                    quantity = _text(pack.find("s:Quantity", NS))
                    subsidy = _decimal(pack.find("s:Subsidy", NS))
                    label_parts = (chemical_name, formulation_name, brand_name)
                    label = " | ".join(part for part in label_parts if part)
                    records.append(
                        ScheduleItemRecord(
                            source_id="nz_pharmac",
                            jurisdiction="New Zealand",
                            domain="medicines_devices",
                            code_system="PHARMAC pack ID",
                            item_code=pack_id,
                            item_label=label,
                            payment_amount=subsidy,
                            currency="NZD" if subsidy is not None else None,
                            payment_unit=f"pack of {quantity}" if quantity else "pack",
                            effective_from=date(2026, 7, 1),
                            provenance=ProvenanceRecord(
                                source_id="nz_pharmac",
                                source_url=SOURCE_URL,
                                source_version="nz_pharmac_schedule_2026_07",
                                licence_class="permissive",
                                transformation_notes=(
                                    "Parsed Chemical/Formulation/Brand/Pack identifiers and "
                                    "published subsidy only; no net-price inference."
                                ),
                            ),
                        )
                    )
    return records


def _text(element: Any | None) -> str | None:
    if element is None:
        return None
    value = (element.text or "").strip()
    return value or None


def _decimal(element: Any | None) -> float | None:
    value = _text(element)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None

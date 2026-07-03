"""Prototype MBS XML parser.

The real MBS XML has changed shape across releases. This parser is deliberately
defensive: it accepts a tiny canonical fixture and a range of likely field names,
then emits the normalised schedule-item contract.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

from defusedxml import ElementTree as ET
from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord
from reimburse_atlas.parsers.normalise import XmlLikeElement, child_text, parse_amount, parse_date

MBS_DOWNLOAD_URL: HttpUrl = cast(
    "HttpUrl",
    "https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/Content/downloads",
)


def _iter_item_elements(root: XmlLikeElement) -> list[XmlLikeElement]:
    candidates: list[XmlLikeElement] = []
    for element in root.iter():
        tag = element.tag.split("}")[-1].lower()
        if tag in {"item", "mbsitem", "scheduleitem"}:
            candidates.append(element)
    return candidates


def parse_mbs_xml(path: Path) -> list[ScheduleItemRecord]:
    """Parse an MBS-like XML file into schedule item records."""
    root = cast("XmlLikeElement", ET.parse(path).getroot())
    records: list[ScheduleItemRecord] = []
    for item in _iter_item_elements(root):
        code = child_text(item, ("itemnum", "item_number", "itemnumber", "code"))
        label = child_text(item, ("itemlabel", "label", "short_description", "descriptor"))
        description = child_text(
            item,
            ("itemdescription", "item_description", "description", "full_description"),
        )
        if code is None:
            continue
        item_label = label or description or f"MBS item {code}"
        effective_from = parse_date(
            child_text(item, ("startdate", "itemstartdate", "effective_from"))
        )
        records.append(
            ScheduleItemRecord(
                source_id="au_mbs",
                jurisdiction="Australia",
                domain=child_text(item, ("domain", "category")) or "medical_services",
                code_system="MBS",
                item_code=code,
                item_label=item_label,
                item_description=description,
                payment_amount=parse_amount(
                    child_text(item, ("schedulefee", "fee", "benefit", "amount"))
                ),
                currency="AUD",
                payment_unit="item",
                effective_from=effective_from,
                restriction_text=child_text(item, ("restriction", "note", "annotation")),
                setting=child_text(item, ("setting", "location")),
                professional_component=True,
                facility_component=False,
                provenance=ProvenanceRecord(
                    source_id="au_mbs",
                    source_url=MBS_DOWNLOAD_URL,
                    effective_date=effective_from,
                    source_version="au_mbs_seed_fixture",
                    licence_class="public_reuse_unclear",
                    transformation_notes=f"Parsed from local MBS XML-like file: {path.name}.",
                ),
            )
        )
    return records

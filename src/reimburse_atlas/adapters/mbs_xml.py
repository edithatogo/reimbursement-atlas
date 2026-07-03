"""MBS XML fixture adapter.

The live MBS XML structure varies across publication vintages. This adapter is a
contract-first parser for a minimal fixture shape and a compatibility layer for
future source-specific extraction code.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import cast

from defusedxml import ElementTree as ET

from reimburse_atlas.adapters.base import AdapterError, ParsedPayload, require_file
from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord
from reimburse_atlas.parsers.normalise import XmlLikeElement, child_text


class MbsXmlFixtureAdapter:
    """Parse a tiny MBS-like XML fixture into schedule item records."""

    source_id = "au_mbs"
    name = "mbs_xml_fixture"
    supported_formats = ("xml",)

    def parse_file(self, path: Path) -> ParsedPayload:
        """Parse a synthetic MBS XML fixture."""
        require_file(path)
        try:
            root = cast("XmlLikeElement", ET.parse(path).getroot())
        except Exception as exc:
            msg = f"Could not parse XML fixture: {path}"
            raise AdapterError(msg) from exc

        items: list[ScheduleItemRecord] = []
        for node in _iter_item_nodes(root):
            code = child_text(node, ("code",))
            label = child_text(node, ("label",))
            if code is None or label is None:
                msg = f"MBS fixture item is missing code or label in {path}"
                raise AdapterError(msg)
            amount_text = child_text(node, ("schedule_fee",))
            effective_text = child_text(node, ("effective_from",))
            items.append(
                ScheduleItemRecord(
                    source_id=self.source_id,
                    jurisdiction="Australia",
                    domain=child_text(node, ("domain",)) or "medical_services",
                    code_system="MBS",
                    item_code=code,
                    item_label=label,
                    item_description=child_text(node, ("description",)),
                    payment_amount=float(amount_text) if amount_text else None,
                    currency=child_text(node, ("currency",)) or "AUD",
                    payment_unit=child_text(node, ("payment_unit",)) or "item",
                    effective_from=date.fromisoformat(effective_text) if effective_text else None,
                    restriction_text=child_text(node, ("restriction_text",)),
                    setting=child_text(node, ("setting",)),
                    professional_component=True,
                    facility_component=False,
                    provenance=ProvenanceRecord(
                        source_id=self.source_id,
                        source_version=child_text(node, ("source_version",)) or "synthetic_fixture",
                        transformation_notes=(
                            "Parsed from synthetic MBS XML parser-contract fixture."
                        ),
                    ),
                )
            )
        if not items:
            msg = f"No <item> records found in {path}"
            raise AdapterError(msg)
        return ParsedPayload(schedule_items=tuple(items))


def _iter_item_nodes(root: XmlLikeElement) -> list[XmlLikeElement]:
    """Return item-like descendants from an XML-like tree."""
    nodes: list[XmlLikeElement] = []
    for element in root.iter():
        if element.tag.split("}")[-1].lower() == "item":
            nodes.append(element)
    return nodes

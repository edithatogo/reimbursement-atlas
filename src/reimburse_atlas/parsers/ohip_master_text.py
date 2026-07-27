"""Parser for Ontario's public fixed-width OHIP master text file."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import cast

from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord

SOURCE_URL = cast(
    "HttpUrl",
    "https://ontario.ca/files/2026-06/moh-ohip-fee-schedule-master-text-2026-06-02.zip",
)


def parse_ohip_master_text(path: Path) -> list[ScheduleItemRecord]:
    """Parse code, dates, and the first positive published fee per service."""
    records: list[ScheduleItemRecord] = []
    for line in path.read_text(encoding="ascii").splitlines():
        if len(line) < 29:
            continue
        code = line[:4].strip()
        effective = _date(line[4:12])
        termination = _date(line[12:20])
        fees = [_fee(line[offset : offset + 8]) for offset in range(20, len(line), 8)]
        payment = next((fee for fee in fees if fee is not None and fee > 0), None)
        if not code or effective is None:
            continue
        records.append(
            ScheduleItemRecord(
                source_id="ca_on_ohip",
                jurisdiction="Ontario, Canada",
                domain="medical_services",
                code_system="OHIP service code",
                item_code=code,
                item_label=f"OHIP service {code}",
                payment_amount=payment,
                currency="CAD" if payment is not None else None,
                effective_from=effective,
                effective_to=termination,
                provenance=ProvenanceRecord(
                    source_id="ca_on_ohip",
                    source_url=SOURCE_URL,
                    source_version="ca_on_ohip_master_text_2026_06_02",
                    licence_class="permissive",
                    transformation_notes=(
                        "Parsed fixed-width service code, effective dates, and first positive "
                        "published fee; descriptors are not present in the master text file."
                    ),
                ),
            )
        )
    return records


def _date(value: str) -> date | None:
    if value == "99999999":
        return None
    try:
        return date.fromisoformat(f"{value[:4]}-{value[4:6]}-{value[6:]}")
    except ValueError:
        return None


def _fee(value: str) -> float | None:
    try:
        return int(value) / 100
    except ValueError:
        return None

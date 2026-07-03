"""Prototype CMS Clinical Laboratory Fee Schedule CSV parser."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import cast

from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord
from reimburse_atlas.parsers.normalise import clean_text, first_present, parse_amount

CLFS_URL: HttpUrl = cast(
    "HttpUrl",
    "https://www.cms.gov/medicare/payment/fee-schedules/clinical-laboratory-fee-schedule-clfs",
)


def parse_cms_clfs_csv(path: Path) -> list[ScheduleItemRecord]:
    """Parse a CLFS-like CSV into schedule item records.

    CPT/HCPCS descriptors may carry redistribution constraints. Fixtures should
    use synthetic or short non-proprietary labels unless licence review allows
    committing more text.
    """
    records: list[ScheduleItemRecord] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            code = clean_text(first_present(row, ("hcpcs", "hcpcs_code", "code", "cpt")))
            if code is None:
                continue
            label = clean_text(first_present(row, ("short_label", "label", "description")))
            amount = parse_amount(first_present(row, ("payment_rate", "rate", "national_limit")))
            records.append(
                ScheduleItemRecord(
                    source_id="us_cms_clfs",
                    jurisdiction="United States",
                    domain="laboratory",
                    code_system="HCPCS_CLFS",
                    item_code=code,
                    item_label=label or f"CLFS item {code}",
                    item_description=clean_text(
                        first_present(row, ("non_proprietary_description",))
                    ),
                    payment_amount=amount,
                    currency="USD",
                    payment_unit="item",
                    setting="outpatient",
                    professional_component=False,
                    facility_component=False,
                    provenance=ProvenanceRecord(
                        source_id="us_cms_clfs",
                        source_url=CLFS_URL,
                        source_version="us_cms_clfs_seed_fixture",
                        licence_class="public_reuse_unclear",
                        transformation_notes=f"Parsed from local CLFS-like CSV file: {path.name}.",
                    ),
                )
            )
    return records

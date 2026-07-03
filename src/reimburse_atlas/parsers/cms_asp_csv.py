"""Prototype CMS Average Sales Price drug-pricing CSV parser."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import cast

from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord
from reimburse_atlas.parsers.normalise import clean_text, first_present, parse_amount, parse_date

ASP_URL: HttpUrl = cast(
    "HttpUrl",
    (
        "https://www.cms.gov/medicare/payment/fee-for-service-providers/part-b-drugs/"
        "average-drug-sales-price"
    ),
)


def parse_cms_asp_csv(path: Path) -> list[ScheduleItemRecord]:
    """Parse a CMS ASP-like CSV into schedule item records."""
    records: list[ScheduleItemRecord] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            code = clean_text(first_present(row, ("hcpcs_code", "hcpcs", "code")))
            if code is None:
                continue
            label = clean_text(first_present(row, ("short_description", "drug_name", "label")))
            effective_from = parse_date(
                first_present(row, ("effective_date", "quarter_start", "effective_from"))
            )
            records.append(
                ScheduleItemRecord(
                    source_id="us_cms_asp",
                    jurisdiction="United States",
                    domain="medicines",
                    code_system="HCPCS_ASP",
                    item_code=code,
                    item_label=label or f"ASP item {code}",
                    item_description=clean_text(
                        first_present(row, ("long_description", "description", "billing_unit"))
                    ),
                    payment_amount=parse_amount(
                        first_present(
                            row,
                            ("payment_limit", "asp_payment_limit", "allowed_amount", "rate"),
                        )
                    ),
                    currency="USD",
                    payment_unit=clean_text(first_present(row, ("billing_unit", "unit")))
                    or "billing_unit",
                    effective_from=effective_from,
                    restriction_text=clean_text(first_present(row, ("notes", "restriction"))),
                    setting="part_b",
                    professional_component=False,
                    facility_component=False,
                    provenance=ProvenanceRecord(
                        source_id="us_cms_asp",
                        source_url=ASP_URL,
                        effective_date=effective_from,
                        source_version="us_cms_asp_seed_fixture",
                        licence_class="public_reuse_unclear",
                        transformation_notes=(
                            f"Parsed from local CMS ASP-like CSV file: {path.name}."
                        ),
                    ),
                )
            )
    return records

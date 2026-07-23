"""Prototype CMS Average Sales Price drug-pricing CSV parser."""

from __future__ import annotations

import csv
import io
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


def parse_cms_asp_csv(
    path: Path,
    *,
    source_version: str = "us_cms_asp_seed_fixture",
    retrieved_at: str | None = None,
) -> list[ScheduleItemRecord]:
    """Parse fixture or official Section 508 CMS ASP CSV rows."""
    records: list[ScheduleItemRecord] = []
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    lines = text.splitlines()
    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if "hcpcs code" in line.casefold() and "payment limit" in line.casefold()
        ),
        0,
    )
    with io.StringIO("\n".join(lines[header_index:]), newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            normalised = {
                str(key).strip().casefold().replace(" ", "_"): value
                for key, value in row.items()
                if key is not None
            }
            code = clean_text(first_present(normalised, ("hcpcs_code", "hcpcs", "code")))
            if code is None:
                continue
            label = clean_text(
                first_present(normalised, ("short_description", "drug_name", "label"))
            )
            effective_from = parse_date(
                first_present(normalised, ("effective_date", "quarter_start", "effective_from"))
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
                        first_present(
                            normalised,
                            (
                                "long_description",
                                "description",
                                "hcpcs_code_dosage",
                                "billing_unit",
                            ),
                        )
                    ),
                    payment_amount=parse_amount(
                        first_present(
                            normalised,
                            ("payment_limit", "asp_payment_limit", "allowed_amount", "rate"),
                        )
                    ),
                    currency="USD",
                    payment_unit=clean_text(
                        first_present(normalised, ("hcpcs_code_dosage", "billing_unit", "unit"))
                    )
                    or "billing_unit",
                    effective_from=effective_from,
                    restriction_text=clean_text(
                        first_present(normalised, ("notes", "restriction"))
                    ),
                    setting="part_b",
                    professional_component=False,
                    facility_component=False,
                    provenance=ProvenanceRecord(
                        source_id="us_cms_asp",
                        source_url=ASP_URL,
                        retrieved_at=retrieved_at,
                        effective_date=effective_from,
                        source_version=source_version,
                        licence_class="permissive",
                        transformation_notes=(
                            "Parsed public CMS Medicare Part B payment-limit fields from "
                            f"local CSV file {path.name}; payment limits are not coverage or "
                            "confidential manufacturer ASP."
                        ),
                    ),
                )
            )
    return records

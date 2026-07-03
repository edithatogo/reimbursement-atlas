"""Prototype PBS API/CSV parser.

The live PBS API exposes many relational tables. This parser targets a denormalised
``items``/``items-overview``-style CSV export or a curated local extract. It is
suitable for parser-contract validation and for later API table joins, but it
must not be interpreted as effective net Commonwealth price where confidential
rebates or deeds apply.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import cast

from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord
from reimburse_atlas.parsers.normalise import clean_text, first_present, parse_amount, parse_date

PBS_API_URL: HttpUrl = cast("HttpUrl", "https://data.pbs.gov.au/document/91327.html")


def parse_pbs_csv(path: Path) -> list[ScheduleItemRecord]:
    """Parse a PBS item overview-like CSV into schedule item records."""
    records: list[ScheduleItemRecord] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            code = clean_text(
                first_present(row, ("pbs_item_code", "item_code", "pbs_code", "li_item_id"))
            )
            if code is None:
                continue
            label = clean_text(
                first_present(row, ("drug_name", "pbs_preferred_term", "brand_name", "name"))
            )
            amount = parse_amount(
                first_present(
                    row,
                    (
                        "dispensed_price_max_quantity",
                        "dpmq",
                        "price",
                        "benefit_amount",
                        "maximum_price",
                    ),
                )
            )
            effective_from = parse_date(
                first_present(row, ("effective_date", "schedule_date", "effective_from"))
            )
            records.append(
                ScheduleItemRecord(
                    source_id="au_pbs",
                    jurisdiction="Australia",
                    domain="medicines",
                    code_system="PBS",
                    item_code=code,
                    item_label=label or f"PBS item {code}",
                    item_description=clean_text(
                        first_present(row, ("form_strength", "description", "presentation"))
                    ),
                    payment_amount=amount,
                    currency="AUD",
                    payment_unit=clean_text(first_present(row, ("payment_unit", "unit"))) or "pack",
                    patient_amount=parse_amount(
                        first_present(row, ("general_patient_charge", "patient_contribution"))
                    ),
                    effective_from=effective_from,
                    restriction_text=clean_text(
                        first_present(
                            row,
                            ("restriction", "restriction_text", "authority_required"),
                        )
                    ),
                    setting="pharmacy",
                    professional_component=False,
                    facility_component=False,
                    provenance=ProvenanceRecord(
                        source_id="au_pbs",
                        source_url=PBS_API_URL,
                        effective_date=effective_from,
                        source_version="au_pbs_seed_fixture",
                        licence_class="public_reuse_unclear",
                        transformation_notes=(
                            f"Parsed from local PBS API/CSV-like extract: {path.name}; "
                            "published amount is not assumed to be net effective price."
                        ),
                    ),
                )
            )
    return records

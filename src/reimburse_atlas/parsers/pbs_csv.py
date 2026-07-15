"""Prototype PBS API/CSV parser.

The live PBS API exposes many relational tables. This parser targets a denormalised
``items``/``items-overview``-style CSV export or a curated local extract. It is
suitable for parser-contract validation and for later API table joins, but it
must not be interpreted as effective net Commonwealth price where confidential
rebates or deeds apply.
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import cast

from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord
from reimburse_atlas.parsers.normalise import clean_text, first_present, parse_amount, parse_date

PBS_API_URL: HttpUrl = cast("HttpUrl", "https://data-api.health.gov.au/pbs/api/v3")


def parse_pbs_csv(path: Path) -> list[ScheduleItemRecord]:
    """Parse a PBS item overview-like CSV into schedule item records."""
    return _parse_rows(path, schedule_dates={})


def parse_pbs_api_csv(path: Path, schedules_path: Path) -> list[ScheduleItemRecord]:
    """Parse a live PBS items CSV using effective dates from a schedules JSON response."""
    payload = cast("dict[str, object]", json.loads(schedules_path.read_text(encoding="utf-8")))
    raw_rows = payload.get("data", [])
    if not isinstance(raw_rows, list):
        msg = "PBS schedules response must contain a data list"
        raise TypeError(msg)
    rows = cast("list[object]", raw_rows)
    schedule_dates: dict[str, date] = {}
    for raw_row in rows:
        if not isinstance(raw_row, dict):
            continue
        row = cast("dict[str, object]", raw_row)
        schedule_code = clean_text(str(row.get("schedule_code", "")))
        effective_date = parse_date(clean_text(str(row.get("effective_date", ""))))
        if schedule_code and effective_date:
            schedule_dates[schedule_code] = effective_date
    if not schedule_dates:
        msg = "PBS schedules response contains no usable schedule dates"
        raise ValueError(msg)
    return _parse_rows(path, schedule_dates=schedule_dates)


def _parse_rows(path: Path, *, schedule_dates: dict[str, date]) -> list[ScheduleItemRecord]:
    """Parse rows while optionally joining schedule codes to effective dates."""
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
                        "determined_price",
                        "claimed_price",
                        "proportional_price",
                    ),
                )
            )
            effective_from = parse_date(
                first_present(row, ("effective_date", "schedule_date", "effective_from"))
            )
            schedule_code = clean_text(first_present(row, ("schedule_code",)))
            if effective_from is None and schedule_code:
                effective_from = schedule_dates.get(schedule_code)
            records.append(
                ScheduleItemRecord(
                    source_id="au_pbs",
                    jurisdiction="Australia",
                    domain="medicines",
                    code_system="PBS",
                    item_code=code,
                    item_label=label or f"PBS item {code}",
                    item_description=clean_text(
                        first_present(
                            row,
                            (
                                "form_strength",
                                "description",
                                "presentation",
                                "li_form",
                                "schedule_form",
                            ),
                        )
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
                            (
                                "restriction",
                                "restriction_text",
                                "authority_required",
                                "legal_car_ind",
                                "legal_unar_ind",
                            ),
                        )
                    ),
                    setting="pharmacy",
                    professional_component=False,
                    facility_component=False,
                    provenance=ProvenanceRecord(
                        source_id="au_pbs",
                        source_url=PBS_API_URL,
                        effective_date=effective_from,
                        source_version=(
                            "au_pbs_api_v3_current_month"
                            if schedule_dates
                            else "au_pbs_seed_fixture"
                        ),
                        licence_class="public_reuse_unclear",
                        transformation_notes=(
                            f"Parsed from local PBS API/CSV-like extract: {path.name}; "
                            "published amount is not assumed to be net effective price."
                        ),
                    ),
                )
            )
    return records

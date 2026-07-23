"""Prototype CMS Physician Fee Schedule CSV parser."""

from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path
from typing import cast

from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord
from reimburse_atlas.parsers.normalise import clean_text, first_present, parse_amount, parse_date

PFS_URL: HttpUrl = cast("HttpUrl", "https://www.cms.gov/medicare/physician-fee-schedule")


def _select_payment_amount(row: Mapping[str, object]) -> float | None:
    """Prefer non-facility price when available, falling back to other payment fields."""
    return parse_amount(
        first_present(
            row,
            (
                "nonfacility_price",
                "non_facility_price",
                "national_non_facility_amount",
                "payment_amount",
                "allowed_amount",
                "rate",
                "facility_price",
            ),
        )
    )


def parse_cms_pfs_csv(
    path: Path,
    *,
    source_version: str = "us_cms_pfs_seed_fixture",
    retrieved_at: str | None = None,
) -> list[ScheduleItemRecord]:
    """Parse a CMS PFS-like CSV into schedule item records.

    CPT/HCPCS descriptors need licence review before redistribution. Public
    fixtures should use synthetic or minimal labels.
    """
    records: list[ScheduleItemRecord] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            code = clean_text(first_present(row, ("hcpcs_code", "hcpcs", "cpt", "code")))
            if code is None:
                continue
            label = clean_text(first_present(row, ("short_description", "label", "description")))
            effective_from = parse_date(
                first_present(row, ("effective_date", "effective_from", "calendar_year"))
            )
            setting = (
                clean_text(first_present(row, ("setting", "site_of_service"))) or "professional"
            )
            records.append(
                ScheduleItemRecord(
                    source_id="us_cms_pfs",
                    jurisdiction="United States",
                    domain="medical_services",
                    code_system="HCPCS_PFS",
                    item_code=code,
                    item_label=label or f"PFS item {code}",
                    item_description=clean_text(
                        first_present(row, ("non_proprietary_description", "notes"))
                    ),
                    payment_amount=_select_payment_amount(row),
                    currency="USD",
                    payment_unit="service",
                    effective_from=effective_from,
                    restriction_text=clean_text(
                        first_present(row, ("status_indicator", "restriction")),
                    ),
                    setting=setting,
                    professional_component=True,
                    facility_component=False,
                    provenance=ProvenanceRecord(
                        source_id="us_cms_pfs",
                        source_url=PFS_URL,
                        retrieved_at=retrieved_at,
                        effective_date=effective_from,
                        source_version=source_version,
                        licence_class="public_reuse_unclear",
                        transformation_notes=(
                            f"Parsed from local CMS PFS-like CSV file: {path.name}; "
                            "CPT descriptor redistribution requires separate licence review."
                        ),
                    ),
                )
            )
    return records


def parse_cms_pfs_carrier_csv(
    path: Path,
    *,
    source_version: str,
    retrieved_at: str | None = None,
) -> list[ScheduleItemRecord]:
    """Parse CMS carrier pricing rows without redistributing CPT descriptors."""
    records: list[ScheduleItemRecord] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.reader(handle):
            if len(row) < 16:
                continue
            year, carrier, locality, code, modifier = (value.strip() for value in row[:5])
            if not code or not year.isdigit():
                continue
            nonfacility = parse_amount(row[5])
            facility = parse_amount(row[6])
            status = clean_text(row[9])
            records.append(
                ScheduleItemRecord(
                    source_id="us_cms_pfs",
                    jurisdiction="United States",
                    domain="medical_services",
                    code_system="HCPCS_PFS",
                    item_code=code,
                    item_label=f"PFS code {code}",
                    payment_amount=nonfacility if nonfacility is not None else facility,
                    currency="USD",
                    payment_unit="service",
                    effective_from=parse_date(f"{year}-01-01"),
                    restriction_text=f"status={status}" if status else None,
                    setting=f"carrier={carrier};locality={locality};modifier={modifier or 'none'}",
                    professional_component=True,
                    facility_component=False,
                    provenance=ProvenanceRecord(
                        source_id="us_cms_pfs",
                        source_url=PFS_URL,
                        retrieved_at=retrieved_at,
                        effective_date=parse_date(f"{year}-01-01"),
                        source_version=source_version,
                        licence_class="public_reuse_unclear",
                        transformation_notes=(
                            "Parsed CMS carrier pricing public numeric fields; CPT descriptors "
                            "are intentionally excluded from this derived bundle."
                        ),
                    ),
                )
            )
    return records

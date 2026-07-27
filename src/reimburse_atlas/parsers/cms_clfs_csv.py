"""Prototype CMS Clinical Laboratory Fee Schedule CSV parser."""

from __future__ import annotations

import csv
import hashlib
import io
from datetime import date
from pathlib import Path
from typing import cast

from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord
from reimburse_atlas.parsers.normalise import clean_text, first_present, parse_amount, parse_date

CLFS_URL: HttpUrl = cast(
    "HttpUrl",
    "https://www.cms.gov/medicare/payment/fee-schedules/clinical-laboratory-fee-schedule-clfs",
)


def _parse_clfs_date(value: str | None) -> date | None:
    cleaned = clean_text(value)
    if cleaned is not None and len(cleaned) == 8 and cleaned.isdigit():
        return date(int(cleaned[:4]), int(cleaned[4:6]), int(cleaned[6:]))
    return parse_date(cleaned)


def parse_cms_clfs_csv(  # ruff:ignore[too-many-locals]
    path: Path,
    *,
    source_version: str = "us_cms_clfs_seed_fixture",
    retrieved_at: str | None = None,
    restricted_numeric_only: bool = False,
) -> list[ScheduleItemRecord]:
    """Parse a CLFS-like CSV into schedule item records.

    CPT/HCPCS descriptors may carry redistribution constraints. Fixtures should
    use synthetic or short non-proprietary labels unless licence review allows
    committing more text.
    """
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
            if "hcpcs" in line.casefold() and "rate" in line.casefold()
        ),
        0,
    )
    with io.StringIO("\n".join(lines[header_index:]), newline="") as handle:
        reader = csv.DictReader(handle)
        for row_index, row in enumerate(reader, start=1):
            normalised = {
                str(key).strip().casefold().replace(" ", "_"): value
                for key, value in row.items()
                if key is not None
            }
            code = clean_text(
                first_present(normalised, ("hcpcs", "hcpcs_code", "code", "cpt"))
            )
            if code is None:
                continue
            label = clean_text(
                first_present(normalised, ("short_label", "label", "description", "shortdesc"))
            )
            amount = parse_amount(
                first_present(normalised, ("payment_rate", "rate", "national_limit"))
            )
            effective_from = _parse_clfs_date(
                first_present(normalised, ("eff_date", "effective_date", "effective_from"))
            )
            if restricted_numeric_only:
                row_fingerprint = hashlib.sha256(
                    f"{source_version}:{row_index}".encode()
                ).hexdigest()[:16]
                item_code = f"CLFS_DERIVED_{row_fingerprint}"
                item_label = "CLFS numeric payment row"
                item_description = None
                code_system = "CLFS_DERIVED_ROW"
            else:
                item_code = code
                item_label = label or f"CLFS item {code}"
                item_description = clean_text(
                    first_present(normalised, ("non_proprietary_description",))
                )
                code_system = "HCPCS_CLFS"
            records.append(
                ScheduleItemRecord(
                    source_id="us_cms_clfs",
                    jurisdiction="United States",
                    domain="laboratory",
                    code_system=code_system,
                    item_code=item_code,
                    item_label=item_label,
                    item_description=item_description,
                    payment_amount=amount,
                    currency="USD",
                    payment_unit="item",
                    effective_from=effective_from,
                    setting="outpatient",
                    professional_component=False,
                    facility_component=False,
                    provenance=ProvenanceRecord(
                        source_id="us_cms_clfs",
                        source_url=CLFS_URL,
                        retrieved_at=retrieved_at,
                        effective_date=effective_from,
                        source_version=source_version,
                        licence_class=(
                            "restricted" if restricted_numeric_only else "public_reuse_unclear"
                        ),
                        transformation_notes=(
                            "Parsed numeric payment fields in restricted mode; CPT/HCPCS "
                            "identifiers and all descriptor text were excluded."
                            if restricted_numeric_only
                            else f"Parsed from local CLFS-like CSV file: {path.name}."
                        ),
                    ),
                )
            )
    return records

"""Parser for bounded public prices in the NHS Payment Scheme workbook."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import cast

import polars as pl
from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord

SOURCE_URL = cast(
    "HttpUrl",
    "https://www.england.nhs.uk/wp-content/uploads/2026/03/"
    "26-27-NHSPS-Annex-A-Prices-workbook.xlsx",
)
REQUIRED = {
    "TMC",
    "Test Method",
    "Cancer / Rare Disease Test Price (£)",
    "Cancer Report Price (£)",
    "Rare Disease Report Price (£)",
}


def parse_nhs_payment_scheme_xlsx(path: Path) -> list[ScheduleItemRecord]:
    """Parse the explicitly labelled genomics guide-price sheet."""
    frame = pl.read_excel(
        path,
        sheet_name="4b Genomics prices",
        read_options={"header_row": 6},
    )
    missing = REQUIRED - set(frame.columns)
    if missing:
        msg = f"NHS payment workbook schema drift; missing columns: {sorted(missing)}"
        raise ValueError(msg)
    records: list[ScheduleItemRecord] = []
    price_columns = (
        ("test", "Cancer / Rare Disease Test Price (£)"),
        ("cancer report", "Cancer Report Price (£)"),
        ("rare-disease report", "Rare Disease Report Price (£)"),
    )
    for index, row in enumerate(frame.iter_rows(named=True), start=1):
        code = _text(row.get("TMC"))
        method = _text(row.get("Test Method"))
        if not code or not method:
            continue
        for component, column in price_columns:
            price = _price(row.get(column))
            if price is None:
                continue
            records.append(
                ScheduleItemRecord(
                    source_id="uk_nhs_payment_scheme",
                    jurisdiction="England",
                    domain="genomics",
                    code_system="NHS TMC",
                    item_code=f"{code}_{component.replace(' ', '_')}_{index}",
                    item_label=f"{method} ({component})",
                    payment_amount=price,
                    currency="GBP",
                    payment_unit="guide price",
                    effective_from=date(2026, 4, 1),
                    provenance=ProvenanceRecord(
                        source_id="uk_nhs_payment_scheme",
                        source_url=SOURCE_URL,
                        source_version="uk_nhs_payment_scheme_2026_27_annex_a",
                        licence_class="public_reuse_unclear",
                        transformation_notes=(
                            "Parsed only numeric values from the labelled genomics guide-price "
                            "sheet; no coverage, cost, or cross-system equivalence inference."
                        ),
                    ),
                )
            )
    return records


def _text(value: object) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None


def _price(value: object) -> float | None:
    if isinstance(value, int | float):
        return float(value) if value >= 0 else None
    text = _text(value)
    if text is None:
        return None
    try:
        return float(text.replace(",", "").replace("£", ""))
    except ValueError:
        return None

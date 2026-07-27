"""Parser for the live NHS rare-disease Genomic Test Directory workbook."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import polars as pl
from pydantic import HttpUrl

from reimburse_atlas.contracts import CoverageDecisionRecord, ProvenanceRecord

SOURCE_URL = cast(
    "HttpUrl",
    "https://www.england.nhs.uk/publication/national-genomic-test-directories/",
)
REQUIRED = {"Clinical indication ID", "Test ID", "Clinical Indication"}


def parse_nhs_genomic_directory_xlsx(path: Path) -> list[CoverageDecisionRecord]:
    """Parse commissioned rare-disease test rows without overstating coverage."""
    frame = pl.read_excel(path, sheet_name="R&ID indications")
    missing = REQUIRED - set(frame.columns)
    if missing:
        msg = f"NHS genomic workbook schema drift; missing columns: {sorted(missing)}"
        raise ValueError(msg)
    records: list[CoverageDecisionRecord] = []
    for row in frame.iter_rows(named=True):
        indication_id = _value(row.get("Clinical indication ID"))
        test_id = _value(row.get("Test ID"))
        indication = _value(row.get("Clinical Indication"))
        if not indication_id or not test_id or not indication:
            continue
        method = _value(row.get("Test Method"))
        category = _value(row.get("Commissioning category"))
        records.append(
            CoverageDecisionRecord(
                source_id="uk_genomic_test_directory",
                decision_id=test_id,
                jurisdiction="England",
                technology_name=indication,
                technology_domain="genomics",
                decision_status="covered_with_restrictions",
                evidence_standard="NHS commissioned test-directory listing",
                restriction_summary=(
                    f"Clinical indication {indication_id}; commissioning category "
                    f"{category or 'not stated'}; method {method or 'not stated'}."
                ),
                provenance=ProvenanceRecord(
                    source_id="uk_genomic_test_directory",
                    source_url=SOURCE_URL,
                    source_version="uk_genomic_test_directory_rare_v9",
                    licence_class="public_reuse_unclear",
                    transformation_notes=(
                        "Parsed commissioned indication and test metadata from the official "
                        "workbook; listing is not represented as universal patient coverage."
                    ),
                ),
            )
        )
    return records


def _value(value: object) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None

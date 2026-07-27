"""Parser for public CMS Medicare Coverage Database NCD exports."""

from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
from typing import cast

from pydantic import HttpUrl

from reimburse_atlas.contracts import CoverageDecisionRecord, ProvenanceRecord

SOURCE_URL = cast(
    "HttpUrl",
    "https://downloads.cms.gov/medicare-coverage-database/downloads/exports/ncd.zip",
)
REQUIRED = {"NCD_id", "NCD_vrsn_num", "NCD_mnl_sect_title", "natl_cvrg_type"}


def parse_cms_mcd_ncd_csv(path: Path) -> list[CoverageDecisionRecord]:
    """Parse stable NCD identity and status fields, excluding long document text."""
    records: list[CoverageDecisionRecord] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or ())
        if missing:
            msg = f"CMS MCD NCD schema drift; missing columns: {sorted(missing)}"
            raise ValueError(msg)
        for row in reader:
            ncd_id = (row.get("NCD_id") or "").strip()
            version = (row.get("NCD_vrsn_num") or "").strip()
            title = (row.get("NCD_mnl_sect_title") or "").strip()
            if not ncd_id or not version or not title:
                continue
            national = (row.get("natl_cvrg_type") or "").strip().lower() == "true"
            terminated = bool((row.get("NCD_trmntn_dt") or "").strip())
            status = "not_covered" if terminated else ("covered" if national else "unknown")
            records.append(
                CoverageDecisionRecord(
                    source_id="us_cms_mcd",
                    decision_id=f"NCD-{ncd_id}-v{version}",
                    jurisdiction="United States",
                    technology_name=title,
                    technology_domain="medicare_coverage",
                    decision_status=status,
                    decision_date=_date(row.get("NCD_efctv_dt")),
                    evidence_standard="CMS National Coverage Determination",
                    restriction_summary="National NCD export metadata; consult the cited NCD.",
                    provenance=ProvenanceRecord(
                        source_id="us_cms_mcd",
                        source_url=SOURCE_URL,
                        source_version="us_cms_mcd_ncd_2026_07_20",
                        licence_class="permissive",
                        transformation_notes=(
                            "Retained NCD identity, title, dates, and national/termination flags; "
                            "excluded long HTML text and did not infer item-level coverage."
                        ),
                    ),
                )
            )
    return records


def _date(value: str | None) -> date | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return None

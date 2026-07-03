"""Prototype NHS Genomic Test Directory parser."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import cast

from pydantic import HttpUrl

from reimburse_atlas.contracts import CoverageDecisionRecord, ProvenanceRecord
from reimburse_atlas.parsers.normalise import clean_text, first_present

GENOMIC_DIRECTORY_URL: HttpUrl = cast(
    "HttpUrl",
    "https://www.england.nhs.uk/publication/national-genomic-test-directories/",
)


def parse_nhs_genomic_directory_csv(path: Path) -> list[CoverageDecisionRecord]:
    """Parse a test-directory-like CSV into coverage-decision records."""
    records: list[CoverageDecisionRecord] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            code = clean_text(first_present(row, ("test_code", "code", "r_code")))
            name = clean_text(first_present(row, ("test_name", "name", "indication")))
            if code is None or name is None:
                continue
            eligibility = clean_text(first_present(row, ("eligibility", "criteria", "restriction")))
            records.append(
                CoverageDecisionRecord(
                    source_id="uk_genomic_test_directory",
                    decision_id=code,
                    jurisdiction="England",
                    technology_name=name,
                    technology_domain="genomics",
                    decision_status="covered_with_restrictions" if eligibility else "covered",
                    evidence_standard="commissioned genomic test directory listing",
                    restriction_summary=eligibility,
                    provenance=ProvenanceRecord(
                        source_id="uk_genomic_test_directory",
                        source_url=GENOMIC_DIRECTORY_URL,
                        source_version="uk_genomic_directory_seed_fixture",
                        licence_class="public_reuse_unclear",
                        transformation_notes=(
                            f"Parsed from local NHS genomic-directory-like CSV file: {path.name}."
                        ),
                    ),
                )
            )
    return records

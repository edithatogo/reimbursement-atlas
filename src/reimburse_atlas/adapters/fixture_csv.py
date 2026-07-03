"""CSV fixture adapters for first-wave source contracts.

The fixtures are deliberately synthetic. They test parser shape without
redistributing restricted third-party descriptors or copyrighted schedule dumps.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from reimburse_atlas.adapters.base import ParsedPayload, non_empty_rows, require_file
from reimburse_atlas.contracts import CoverageDecisionRecord, ProvenanceRecord, ScheduleItemRecord


class CmsClfsFixtureAdapter:
    """Parse a tiny CMS CLFS-like CSV fixture into schedule item records."""

    source_id = "us_cms_clfs"
    name = "cms_clfs_fixture"
    supported_formats = ("csv",)

    def parse_file(self, path: Path) -> ParsedPayload:
        """Parse a synthetic CLFS fixture."""
        require_file(path)
        with path.open(newline="", encoding="utf-8") as handle:
            rows = non_empty_rows(csv.DictReader(handle), path)
        items: list[ScheduleItemRecord] = []
        for row in rows:
            items.append(
                ScheduleItemRecord(
                    source_id=self.source_id,
                    jurisdiction="United States",
                    domain="laboratory",
                    code_system=row.get("code_system", "HCPCS/CPT"),
                    item_code=row["code"],
                    item_label=row["label"],
                    item_description=row.get("description") or None,
                    payment_amount=(
                        float(row["payment_amount"]) if row.get("payment_amount") else None
                    ),
                    currency=row.get("currency") or "USD",
                    payment_unit=row.get("payment_unit") or "test",
                    effective_from=date.fromisoformat(row["effective_from"])
                    if row.get("effective_from")
                    else None,
                    restriction_text=row.get("restriction_text") or None,
                    setting=row.get("setting") or "clinical_laboratory",
                    provenance=ProvenanceRecord(
                        source_id=self.source_id,
                        source_version=row.get("source_version") or "synthetic_fixture",
                        transformation_notes=(
                            "Parsed from synthetic CMS CLFS parser-contract fixture."
                        ),
                    ),
                )
            )
        return ParsedPayload(schedule_items=tuple(items))


class PbsFixtureAdapter:
    """Parse a tiny PBS-like CSV fixture into schedule item records."""

    source_id = "au_pbs"
    name = "pbs_fixture"
    supported_formats = ("csv",)

    def parse_file(self, path: Path) -> ParsedPayload:
        """Parse a synthetic PBS fixture."""
        require_file(path)
        with path.open(newline="", encoding="utf-8") as handle:
            rows = non_empty_rows(csv.DictReader(handle), path)
        items: list[ScheduleItemRecord] = []
        for row in rows:
            items.append(
                ScheduleItemRecord(
                    source_id=self.source_id,
                    jurisdiction="Australia",
                    domain="medicines",
                    code_system=row.get("code_system", "PBS item"),
                    item_code=row["code"],
                    item_label=row["label"],
                    item_description=row.get("description") or None,
                    payment_amount=(
                        float(row["published_price"]) if row.get("published_price") else None
                    ),
                    currency=row.get("currency") or "AUD",
                    payment_unit=row.get("payment_unit") or "dispensed_item",
                    effective_from=date.fromisoformat(row["effective_from"])
                    if row.get("effective_from")
                    else None,
                    restriction_text=row.get("restriction_text") or None,
                    setting=row.get("setting") or "community_or_hospital",
                    provenance=ProvenanceRecord(
                        source_id=self.source_id,
                        source_version=row.get("source_version") or "synthetic_fixture",
                        transformation_notes=(
                            "Parsed from synthetic PBS parser-contract fixture; "
                            "prices are placeholders."
                        ),
                    ),
                )
            )
        return ParsedPayload(schedule_items=tuple(items))


class NhsGenomicDirectoryFixtureAdapter:
    """Parse a tiny NHS genomic test directory fixture into coverage decisions."""

    source_id = "uk_genomic_test_directory"
    name = "nhs_genomic_directory_fixture"
    supported_formats = ("csv",)

    def parse_file(self, path: Path) -> ParsedPayload:
        """Parse a synthetic NHS genomic directory fixture."""
        require_file(path)
        with path.open(newline="", encoding="utf-8") as handle:
            rows = non_empty_rows(csv.DictReader(handle), path)
        decisions: list[CoverageDecisionRecord] = []
        for row in rows:
            decisions.append(
                CoverageDecisionRecord(
                    source_id=self.source_id,
                    decision_id=row["test_code"],
                    jurisdiction="England",
                    technology_name=row["test_name"],
                    technology_domain="genomics",
                    decision_status="covered_with_restrictions"
                    if row.get("eligibility")
                    else "covered",
                    decision_date=date.fromisoformat(row["effective_from"])
                    if row.get("effective_from")
                    else None,
                    evidence_standard=row.get("evidence_standard") or None,
                    restriction_summary=row.get("eligibility") or None,
                    economic_notes=row.get("economic_notes") or None,
                    provenance=ProvenanceRecord(
                        source_id=self.source_id,
                        source_version=row.get("source_version") or "synthetic_fixture",
                        transformation_notes=(
                            "Parsed from synthetic NHS genomic directory parser-contract fixture."
                        ),
                    ),
                )
            )
        return ParsedPayload(coverage_decisions=tuple(decisions))

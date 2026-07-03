"""First-wave ingestion planning utilities.

The atlas separates *planning* from *fetching*. This makes licence checks,
provenance, and reproducibility reviewable before any live source is mirrored or
parsed.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from reimburse_atlas.adapters import SourceAcquisitionPlan
from reimburse_atlas.models import SourceRecord, SourceVersionRecord

PARSER_BY_SOURCE = {
    "au_mbs": "MbsXmlFixtureAdapter -> future live MBS XML adapter",
    "au_pbs": "PbsFixtureAdapter -> future live PBS API/CSV adapter",
    "us_cms_clfs": "CmsClfsFixtureAdapter -> future live CMS CLFS CSV adapter",
    "us_cms_pfs": "planned CMS PFS RVU/fee-schedule adapter",
    "us_cms_asp": "planned CMS ASP drug-pricing adapter",
    "uk_genomic_test_directory": (
        "NhsGenomicDirectoryFixtureAdapter -> future live NHS workbook adapter"
    ),
}

LICENCE_GATE_BY_SOURCE = {
    "au_mbs": "confirm Commonwealth redistribution terms before mirroring raw XML",
    "au_pbs": (
        "confirm PBS API terms and do not represent published prices as net confidential prices"
    ),
    "us_cms_clfs": (
        "avoid redistributing proprietary CPT long descriptors; store derived numeric fields only"
    ),
    "us_cms_pfs": (
        "CPT licence gate required; retain only permitted derived fields in public dataset"
    ),
    "us_cms_asp": "confirm CMS public-file reuse and preserve publication metadata",
    "uk_genomic_test_directory": (
        "confirm NHS publication licence and workbook redistribution status"
    ),
}

CACHE_POLICY_BY_TIER = {
    "tier_1": "versioned-public-cache-after-licence-review",
    "tier_2": "metadata-and-derived-records-first; raw-cache-case-by-case",
    "tier_3": "metadata-only-until-legal-review",
}


def build_first_wave_plans(
    sources: list[SourceRecord], versions: list[SourceVersionRecord]
) -> list[SourceAcquisitionPlan]:
    """Build acquisition plans for registered first-wave source versions."""
    sources_by_id = {source.id: source for source in sources}
    plans: list[SourceAcquisitionPlan] = []
    for version in versions:
        source = sources_by_id.get(version.source_id)
        if source is None:
            continue
        parser_name = PARSER_BY_SOURCE.get(version.source_id, "planned source-specific adapter")
        plans.append(
            SourceAcquisitionPlan(
                source_id=version.source_id,
                version_id=version.id,
                url=version.source_url,
                expected_format=version.format,
                parser_name=parser_name,
                acquisition_mode="manual_fixture_then_reviewed_live_fetch",
                licence_gate=LICENCE_GATE_BY_SOURCE.get(
                    version.source_id,
                    "licence and redistribution review required before mirroring raw data",
                ),
                cache_policy=CACHE_POLICY_BY_TIER[source.access_tier],
                notes=version.notes,
            )
        )
    return plans


@dataclass(frozen=True)
class IngestionReadinessRecord:
    """Source-level readiness record for the ingestion backlog."""

    source_id: str
    parser_name: str
    blocker_count: int
    blockers: str
    recommended_next_action: str


def assess_ingestion_readiness(
    plans: list[SourceAcquisitionPlan],
) -> list[IngestionReadinessRecord]:
    """Create a concise readiness backlog from acquisition plans."""
    records: list[IngestionReadinessRecord] = []
    for plan in plans:
        blockers: list[str] = []
        if "licence" in plan.licence_gate.lower() or "confirm" in plan.licence_gate.lower():
            blockers.append("licence_gate")
        if "fixture" in plan.expected_format.lower():
            blockers.append("live_source_shape_unverified")
        if "planned" in plan.parser_name.lower() and "fixture" not in plan.parser_name.lower():
            blockers.append("parser_not_implemented")
        next_action = (
            "promote fixture parser to live-source prototype"
            if "parser_not_implemented" not in blockers
            else "implement parser contract and tiny fixture"
        )
        records.append(
            IngestionReadinessRecord(
                source_id=plan.source_id,
                parser_name=plan.parser_name,
                blocker_count=len(blockers),
                blockers=";".join(blockers) or "none",
                recommended_next_action=next_action,
            )
        )
    return records


def write_ingestion_plan(plans: list[SourceAcquisitionPlan], output_dir: Path) -> tuple[Path, Path]:
    """Write first-wave acquisition plans as CSV and JSONL."""
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "source_acquisition_plan.csv"
    jsonl_path = output_dir / "source_acquisition_plan.jsonl"
    rows = [plan.model_dump(mode="json") for plan in plans]
    fields = sorted({field for row in rows for field in row})
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    return csv_path, jsonl_path


def write_ingestion_readiness(
    records: list[IngestionReadinessRecord], output_dir: Path
) -> tuple[Path, Path]:
    """Write ingestion readiness records as CSV and JSONL."""
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "ingestion_readiness.csv"
    jsonl_path = output_dir / "ingestion_readiness.jsonl"
    rows = [asdict(record) for record in records]
    fields = list(rows[0]) if rows else ["source_id"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    return csv_path, jsonl_path

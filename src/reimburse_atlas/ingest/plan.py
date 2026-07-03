"""First-wave ingestion planning primitives.

The atlas deliberately separates a *plan* from a *fetch*. A plan is safe to
commit because it contains only source metadata, parser targets and licence
checks. Fetching live public data should be an explicit, logged operation.
"""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from pydantic import Field, HttpUrl

from reimburse_atlas.models import (
    FrozenModel,
    NonEmptyStr,
    SourceId,
    SourceRecord,
    SourceVersionRecord,
)

OutputContract = Literal["ScheduleItemRecord", "CoverageDecisionRecord", "SourceRecord"]
NetworkPolicy = Literal["fixture_only", "manual_download", "live_fetch_allowed"]
LicenceGate = Literal["permissive", "public_reuse_review", "restricted_local_only"]


class IngestionTaskRecord(FrozenModel):
    """A single source-version ingestion task."""

    id: SourceId
    source_id: SourceId
    source_version_id: SourceId
    jurisdiction: NonEmptyStr
    domain: NonEmptyStr
    source_url: HttpUrl
    expected_format: NonEmptyStr
    parser_name: NonEmptyStr
    output_contract: OutputContract
    network_policy: NetworkPolicy
    licence_gate: LicenceGate
    priority: int = Field(ge=1, le=5)
    rationale: NonEmptyStr


FIRST_WAVE_PARSERS: dict[str, tuple[str, OutputContract, int]] = {
    "au_mbs": ("parse_mbs_xml", "ScheduleItemRecord", 1),
    "au_pbs": ("parse_pbs_csv", "ScheduleItemRecord", 2),
    "us_cms_clfs": ("parse_cms_clfs_csv", "ScheduleItemRecord", 1),
    "us_cms_pfs": ("parse_cms_pfs_csv", "ScheduleItemRecord", 2),
    "us_cms_asp": ("parse_cms_asp_csv", "ScheduleItemRecord", 2),
    "uk_genomic_test_directory": ("parse_nhs_genomic_directory_csv", "CoverageDecisionRecord", 1),
}


def licence_gate_for(source: SourceRecord) -> LicenceGate:
    """Derive the conservative licence gate from source metadata."""
    text = f"{source.licence_notes} {source.notes}".lower()
    if "restricted" in text or "umls" in text or "cpt" in text:
        return "restricted_local_only"
    if "confirm" in text or "unclear" in text or "proprietary" in text:
        return "public_reuse_review"
    return "permissive"


def network_policy_for(source: SourceRecord, version: SourceVersionRecord) -> NetworkPolicy:
    """Choose a cautious fetch policy for a source version."""
    if "fixture" in version.id or "synthetic" in version.version_label.lower():
        return "fixture_only"
    if source.access_tier == "tier_1" and source.machine_readable:
        return "live_fetch_allowed"
    return "manual_download"


def build_first_wave_ingestion_plan(
    sources: Iterable[SourceRecord],
    versions: Iterable[SourceVersionRecord],
) -> list[IngestionTaskRecord]:
    """Create deterministic ingestion tasks for first-wave source versions."""
    sources_by_id = {source.id: source for source in sources}
    tasks: list[IngestionTaskRecord] = []
    for version in versions:
        source = sources_by_id.get(version.source_id)
        if source is None or source.id not in FIRST_WAVE_PARSERS:
            continue
        parser_name, output_contract, priority = FIRST_WAVE_PARSERS[source.id]
        tasks.append(
            IngestionTaskRecord(
                id=f"ingest_{version.id}",
                source_id=source.id,
                source_version_id=version.id,
                jurisdiction=source.jurisdiction,
                domain=source.domain,
                source_url=version.source_url,
                expected_format=version.format,
                parser_name=parser_name,
                output_contract=output_contract,
                network_policy=network_policy_for(source, version),
                licence_gate=licence_gate_for(source),
                priority=priority,
                rationale=(
                    "First-wave source selected for the genomics/pathology and "
                    "transparent-fee vertical slice."
                ),
            )
        )
    return sorted(tasks, key=lambda task: (task.priority, task.source_id, task.id))


def write_ingestion_plan(tasks: list[IngestionTaskRecord], output_dir: Path) -> tuple[Path, Path]:
    """Write the ingestion plan as JSONL and CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "first_wave_ingestion_plan.jsonl"
    csv_path = output_dir / "first_wave_ingestion_plan.csv"
    rows = [task.model_dump(mode="json") for task in tasks]
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    fields = sorted({field for row in rows for field in row})
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return jsonl_path, csv_path

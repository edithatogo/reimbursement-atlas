"""Rights-scoped parser for the CMS alpha-numeric HCPCS Level II archive."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from datetime import date
from pathlib import Path

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord
from reimburse_atlas.io import pydantic_rows, write_csv, write_jsonl

_PERMITTED_CODE = re.compile(r"^[A-CE-Z][0-9A-Z]{4}$")


def build_hcpcs_level_ii_bundle(
    archive: Path,
    output_root: Path,
    *,
    version_id: str = "us_cms_hcpcs_level_ii_2026_07",
) -> Path:
    """Build a derived-only bundle while excluding CPT and dental descriptors."""
    archive_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    with zipfile.ZipFile(archive) as package:
        names = sorted(
            name
            for name in package.namelist()
            if name.upper().endswith(".TXT") and "_ANWEB_" in name.upper()
        )
        if len(names) != 1:
            raise ValueError("expected exactly one HCPCS ANWEB fixed-width text member")
        lines = package.read(names[0]).decode("cp1252").splitlines()

    rows, excluded = _parse_lines(lines, version_id=version_id, archive_sha=archive_sha)
    bundle = output_root / f"snapshot_{version_id}_{archive_sha[:12]}"
    bundle.mkdir(parents=True, exist_ok=True)
    stem = f"{version_id}_schedule_items"
    serialized = pydantic_rows(rows)
    write_jsonl(serialized, bundle / f"{stem}.jsonl")
    write_csv(serialized, bundle / f"{stem}.csv")
    evidence = {
        "schema_version": "reviewed-hcpcs-level-ii-bundle-v1",
        "source_id": "us_cms_hcpcs_level_ii",
        "source_version_id": version_id,
        "source_url": (
            "https://www.cms.gov/files/zip/"
            "july-2026-alpha-numeric-hcpcs-file.zip"
        ),
        "raw_sha256": archive_sha,
        "raw_file_copied": False,
        "record_count": len(rows),
        "excluded_record_counts": excluded,
        "licence_scope": (
            "Derived public-use alpha-numeric HCPCS Level II metadata only. "
            "Numeric CPT Level I and D-series dental descriptors are excluded."
        ),
        "transformation": (
            "Read the CMS fixed-width ANWEB member, join type-4 continuation text to "
            "type-3 records, normalize whitespace, and retain only codes matching "
            "^[A-CE-Z][0-9A-Z]{4}$."
        ),
        "review_required_before_publication": True,
    }
    for name in ("validation_report.json", "publication_manifest.json"):
        (bundle / name).write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return bundle


def _parse_lines(
    lines: list[str], *, version_id: str, archive_sha: str
) -> tuple[list[ScheduleItemRecord], dict[str, int]]:
    descriptions: dict[str, list[str]] = {}
    labels: dict[str, str] = {}
    excluded = {"numeric_cpt": 0, "dental_d_series": 0, "malformed": 0}
    for line in lines:
        if len(line) < 91:
            excluded["malformed"] += 1
            continue
        code = line[0:5].strip().upper()
        record_type = line[10:11]
        if code.isdigit():
            if record_type == "3":
                excluded["numeric_cpt"] += 1
            continue
        if code.startswith("D"):
            if record_type == "3":
                excluded["dental_d_series"] += 1
            continue
        if not _PERMITTED_CODE.fullmatch(code) or record_type not in {"3", "4"}:
            continue
        long_text = " ".join(line[11:91].split())
        if record_type == "3":
            descriptions[code] = [long_text] if long_text else []
            short_text = " ".join(line[91:119].split()) if len(line) >= 119 else ""
            labels[code] = short_text or long_text or f"HCPCS {code}"
        elif code in descriptions and long_text:
            descriptions[code].append(long_text)

    provenance = ProvenanceRecord(
        source_id="us_cms_hcpcs_level_ii",
        source_version=version_id,
        source_url=(
            "https://www.cms.gov/files/zip/"
            "july-2026-alpha-numeric-hcpcs-file.zip"
        ),
        retrieved_at="2026-07-23T00:00:00Z",
        licence_class="public_reuse_unclear",
        transformation_notes=(
            "Fixed-width CMS ANWEB parsing; raw SHA-256 "
            f"{archive_sha}; numeric CPT and D-series dental descriptors excluded."
        ),
    )
    rows = [
        ScheduleItemRecord(
            source_id="us_cms_hcpcs_level_ii",
            jurisdiction="United States",
            domain="medical_services",
            code_system="HCPCS_LEVEL_II",
            item_code=code,
            item_label=labels[code],
            item_description=" ".join(descriptions[code]) or None,
            effective_from=date(2026, 7, 1),
            provenance=provenance,
        )
        for code in sorted(descriptions)
    ]
    return rows, excluded

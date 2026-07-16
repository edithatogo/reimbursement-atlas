"""Generate a first-wave source URL and licence review checklist."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root, repo_relative

FIRST_WAVE_SOURCE_IDS = {
    "au_mbs",
    "au_pbs",
    "nhs_genomic_directory",
    "us_cms_asp",
    "us_cms_clfs",
    "us_cms_pfs",
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read JSON object rows from a repository seed file."""
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, dict):
            rows.append(cast("dict[str, Any]", value))
    return rows


def build_checklist(root: Path | None = None) -> list[dict[str, Any]]:
    """Build deterministic review rows from source registry and source-file records."""
    repo = root or project_root()
    registry = {
        str(row["id"]): row
        for row in _read_jsonl(repo / "data" / "seed" / "source_registry.jsonl")
        if str(row.get("id")) in FIRST_WAVE_SOURCE_IDS
    }
    rows: list[dict[str, Any]] = []
    for source_file in _read_jsonl(repo / "data" / "seed" / "source_files.jsonl"):
        source_id = str(source_file.get("source_id", ""))
        if source_id not in FIRST_WAVE_SOURCE_IDS:
            continue
        source = registry.get(source_id, {})
        rows.append({
            "source_file_id": source_file["id"],
            "source_id": source_id,
            "source_version_id": source_file["source_version_id"],
            "file_label": source_file["file_label"],
            "source_url": source_file["source_url"],
            "registry_url": source.get("primary_url", ""),
            "acquisition_mode": source_file["acquisition_mode"],
            "licence_gate": source_file["licence_gate"],
            "url_verification_status": "pending_human_verification",
            "licence_review_status": "pending_human_review",
            "raw_handling": "ignored_local_only",
            "required_evidence": (
                "Record access date, authoritative terms, permitted fields, attribution, "
                "redistribution decision, reviewer and evidence before publication."
            ),
            "licence_notes": source.get("licence_notes", ""),
        })
    return rows


def write_checklist(rows: list[dict[str, Any]], *, output_dir: Path) -> tuple[Path, Path, Path]:
    """Write JSONL, CSV and human review instructions."""
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "source_url_licence_checklist.jsonl"
    jsonl_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    csv_path = output_dir / "source_url_licence_checklist.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        writer.writeheader()
        writer.writerows(rows)
    readme_path = output_dir / "README.md"
    readme_path.write_text(
        """# First-wave source URL and licence checklist

This generated checklist records the exact source-file URLs and registry URLs that
must be checked before a first-wave source moves toward publication. `pending_*`
statuses are intentional: URL reachability and licence interpretation require a
human to inspect the authoritative page and record evidence. Apache-2.0 applies to
project code only and does not relicense source data.

Raw payloads remain in ignored local storage. Do not edit generated rows to simulate
review or approval.
""",
        encoding="utf-8",
    )
    return jsonl_path, csv_path, readme_path


def main() -> None:
    """Generate the checklist from committed source metadata."""
    root = project_root()
    paths = write_checklist(
        build_checklist(root),
        output_dir=root / "data" / "derived" / "source_url_licence_checklist",
    )
    print("Wrote source URL/licence checklist: " + ", ".join(repo_relative(p) for p in paths))


if __name__ == "__main__":
    main()

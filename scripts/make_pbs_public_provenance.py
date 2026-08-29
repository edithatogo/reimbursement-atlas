"""Generate rights-safe public provenance for historical PBS acquisitions."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from reimburse_atlas.registry import project_root

ROOT = project_root()
OUTPUT = ROOT / "data/derived/publication/pbs_provenance"
PBS_COPYRIGHT_URL = "https://www.pbs.gov.au/info/general/copyright"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a JSON Lines object stream."""
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def project_rows(
    targets: list[dict[str, Any]], receipts: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Project source URLs and checksums while excluding raw paths and diagnostics."""
    receipt_by_id = {str(row["id"]): row for row in receipts}
    rows: list[dict[str, Any]] = []
    for target in sorted(targets, key=lambda row: str(row["id"])):
        receipt = receipt_by_id.get(str(target["id"]), {})
        checksum = receipt.get("checksum_sha256")
        rows.append({
            "id": target["id"],
            "source_version_id": target["source_version_id"],
            "archive_period": target.get("archive_period"),
            "archive_page": target["archive_page"],
            "source_url": target["file_url"],
            "file_name": target["file_name"],
            "structured_format": target.get("structured_format"),
            "acquisition_status": receipt.get("status", "not_attempted"),
            "byte_size": receipt.get("byte_size"),
            "checksum_sha256": checksum,
            "source_byte_verified": bool(checksum),
            "licence_gate": target["licence_gate"],
            "rights_source": PBS_COPYRIGHT_URL,
            "raw_redistribution_status": "blocked_pending_explicit_permission",
            "raw_payload_included": False,
            "transformation": "metadata_and_checksum_projection_only",
        })
    return rows


def write_jsonl_csv(rows: list[dict[str, Any]], stem: Path) -> None:
    """Write deterministic public JSONL and CSV projections."""
    stem.parent.mkdir(parents=True, exist_ok=True)
    stem.with_suffix(".jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    fields = sorted({key for row in rows for key in row})
    with stem.with_suffix(".csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Generate PDF, structured-package and archive-variant provenance products."""
    pdf_rows = project_rows(
        load_jsonl(ROOT / "data/seed/historical_pbs_archive_targets.jsonl"),
        load_jsonl(
            ROOT
            / "data/derived/historical_sources/pbs_archive_v1/historical_source_downloads.jsonl"
        ),
    )
    structured_rows = project_rows(
        load_jsonl(ROOT / "data/seed/historical_pbs_structured_archive_targets.jsonl"),
        load_jsonl(
            ROOT / "data/derived/historical_sources/pbs_structured_archive_v1/"
            "historical_source_downloads.jsonl"
        ),
    )
    verification_rows = load_jsonl(
        ROOT / "data/derived/historical_sources/pbs_archive_verification_v1/"
        "pbs_archive_verification.jsonl"
    )
    variant_rows = load_jsonl(
        ROOT / "data/derived/historical_sources/pbs_archive_verification_v1/"
        "internet_archive_variant_receipts.jsonl"
    )
    write_jsonl_csv(pdf_rows, OUTPUT / "pbs_pdf_provenance")
    write_jsonl_csv(structured_rows, OUTPUT / "pbs_structured_provenance")
    write_jsonl_csv(verification_rows, OUTPUT / "pbs_archive_verification")
    write_jsonl_csv(variant_rows, OUTPUT / "pbs_archive_variants")
    summary = {
        "schema_version": "pbs-public-provenance-v1",
        "pdf_target_count": len(pdf_rows),
        "pdf_verified_count": sum(row["source_byte_verified"] for row in pdf_rows),
        "structured_target_count": len(structured_rows),
        "structured_verified_count": sum(row["source_byte_verified"] for row in structured_rows),
        "internet_archive_exact_match_count": sum(
            row.get("verification_status") == "exact_digest_match" for row in verification_rows
        ),
        "internet_archive_variant_count": len(variant_rows),
        "raw_payload_count": 0,
        "raw_publication_status": "blocked_pending_explicit_permission",
        "rights_source": PBS_COPYRIGHT_URL,
        "claim_boundary": (
            "This product publishes source URLs, checksums, archive observations and provenance. "
            "It does not publish raw PBS payloads, grant redistribution rights, establish complete "
            "structured history or authorize research and policy claims."
        ),
    }
    (OUTPUT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()

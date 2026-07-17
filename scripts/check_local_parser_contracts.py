"""Validate source-specific parser contracts against ignored local raw caches."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from reimburse_atlas.parsers.mbs_txt import parse_mbs_txt_pair, parse_stats
from reimburse_atlas.parsers.pbs_csv import parse_pbs_api_csv
from reimburse_atlas.registry import project_root, repo_relative


def _file_metadata(path: Path, root: Path) -> dict[str, object]:
    """Return redacted, checksum-bound metadata for one local cache file."""
    relative = Path(repo_relative(path, root))
    return {
        "path": f"local_raw_only:{relative.parent}/{path.name}",
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _validate_mbs(root: Path) -> dict[str, Any]:
    """Validate the MBS item-map/descriptor parser without exporting source text."""
    item_map = root / "data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT"
    descriptors = root / "data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT"
    if not item_map.exists() or not descriptors.exists():
        return {"status": "skipped", "reason": "ignored MBS pair is absent"}
    stats = parse_stats(item_map, descriptors)
    records = parse_mbs_txt_pair(item_map, descriptors)
    codes = [record.item_code for record in records]
    checks = {
        "item_map_rows_positive": stats.item_map_rows > 0,
        "descriptor_rows_positive": stats.descriptor_rows > 0,
        "joined_rows_positive": stats.joined_rows > 0,
        "parsed_records_positive": len(records) > 0,
        "unique_item_codes": len(codes) == len(set(codes)),
        "records_source_is_au_mbs": all(record.source_id == "au_mbs" for record in records),
    }
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "counts": {
            "item_map_rows": stats.item_map_rows,
            "descriptor_rows": stats.descriptor_rows,
            "joined_rows": stats.joined_rows,
            "descriptor_only_rows": stats.descriptor_only_rows,
            "parsed_records": len(records),
        },
        "files": [_file_metadata(item_map, root), _file_metadata(descriptors, root)],
    }


def _validate_pbs(root: Path) -> dict[str, Any]:
    """Validate the PBS API CSV parser and fee extract shape locally."""
    items = root / "data/raw_live/au_pbs/pbs_v3_items_4706.csv"
    schedules = root / "data/raw_live/au_pbs/pbs_v3_schedules.json"
    fees = root / "data/raw_live/au_pbs/pbs_v3_fees_4706.csv"
    if not items.exists() or not schedules.exists() or not fees.exists():
        return {"status": "skipped", "reason": "ignored PBS extract is absent"}
    records = parse_pbs_api_csv(items, schedules)
    with fees.open(newline="", encoding="utf-8-sig") as handle:
        fee_rows = list(csv.DictReader(handle))
    item_codes = [record.item_code for record in records]
    duplicate_item_codes = len(item_codes) - len(set(item_codes))
    checks = {
        "item_records_positive": len(records) > 0,
        "fee_rows_positive": len(fee_rows) > 0,
        "item_codes_present": all(item_codes),
        "records_source_is_au_pbs": all(record.source_id == "au_pbs" for record in records),
        "effective_dates_present": all(record.effective_from is not None for record in records),
        "fee_schedule_codes_present": all(row.get("schedule_code") == "4706" for row in fee_rows),
    }
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "counts": {
            "item_records": len(records),
            "fee_rows": len(fee_rows),
            "duplicate_item_codes": duplicate_item_codes,
        },
        "files": [
            _file_metadata(items, root),
            _file_metadata(schedules, root),
            _file_metadata(fees, root),
        ],
    }


def build_report(root: Path | None = None) -> dict[str, object]:
    """Build a redacted local parser-contract report."""
    repository = root or project_root()
    sources = {
        "au_mbs_txt_pair": _validate_mbs(repository),
        "au_pbs_api_csv": _validate_pbs(repository),
    }
    statuses = [str(source["status"]) for source in sources.values()]
    return {
        "schema_version": "local-parser-contracts-v1",
        "status": "fail" if "fail" in statuses else ("pass" if "pass" in statuses else "skipped"),
        "network_io": False,
        "mutation_performed": False,
        "licence_approval": False,
        "sources": sources,
    }


def main() -> None:
    """Run local parser contracts and optionally write the redacted report."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="Optional path for the redacted JSON report.")
    args = parser.parse_args()
    report = build_report()
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    if report["status"] == "fail":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

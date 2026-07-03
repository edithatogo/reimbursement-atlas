"""Generate source snapshot records for committed synthetic fixtures."""

from __future__ import annotations

from reimburse_atlas.registry import project_root
from reimburse_atlas.snapshots import build_fixture_snapshots, write_snapshot_records


def main() -> None:
    """Write source snapshot JSONL and CSV seed files."""
    records = build_fixture_snapshots()
    jsonl_path, csv_path = write_snapshot_records(records, project_root() / "data" / "seed")
    print(f"Wrote {len(records)} source snapshots to {jsonl_path} and {csv_path}")


if __name__ == "__main__":
    main()

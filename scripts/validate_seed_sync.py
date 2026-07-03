"""Validate JSONL/CSV seed-file synchronisation."""

from __future__ import annotations

from reimburse_atlas.validation import all_seed_pairs_ok, seed_pair_statuses


def main() -> None:
    """Exit non-zero if any seed CSV mirror is stale."""
    statuses = seed_pair_statuses()
    for status in statuses:
        print(
            f"{status.table_name}: jsonl={status.jsonl_rows} csv={status.csv_rows} ok={status.ok}"
        )
    if not all_seed_pairs_ok(statuses):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

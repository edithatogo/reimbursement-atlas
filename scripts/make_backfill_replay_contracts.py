"""Generate historical MBS/PBS snapshot and deterministic replay evidence."""

from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.backfill_replay import (
    BackfillReplayContract,
    build_replay_plan,
    build_snapshot_records,
)
from reimburse_atlas.registry import project_root, repo_relative


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def main() -> None:
    """Write normative contracts, immutable ledger, replay plan, and summary."""
    root = project_root()
    derived = root / "data/derived/historical_sources"
    rows = _read_jsonl(derived / "historical_source_downloads.jsonl")
    pbs_downloads = derived / "pbs_archive_v1/historical_source_downloads.jsonl"
    if pbs_downloads.is_file():
        rows.extend(_read_jsonl(pbs_downloads))
    catalogue = _read_jsonl(derived / "historical_source_catalog.jsonl")
    known = {(str(row["source_id"]), str(row["source_version_id"])) for row in rows}
    rows.extend(
        row
        for row in catalogue
        if (str(row["source_id"]), str(row["source_version_id"])) not in known
    )
    records = build_snapshot_records(rows)
    contracts = tuple(
        BackfillReplayContract(
            contract_id=f"{source_id}:historical-backfill-replay:v1",
            source_id=source_id,
            partition_identity=("source_id", "archive_period", "logical_asset_id"),
            snapshot_identity=("partition_id", "payload_sha256", "metadata_sha256"),
            idempotency_rule="partition_and_snapshot_sha256",
            late_arrival_rule="append_then_replay_partition",
            correction_rule="new_snapshot_never_overwrite",
            supersession_rule="explicit_acyclic_predecessor",
            replay_order=("partition_id", "correction_sequence", "snapshot_id"),
            deterministic_output_rule="canonical_json_sha256",
            missing_payload_rule="metadata_only_fail_closed",
        )
        for source_id in sorted({row.source_id for row in records})
    )
    output = derived / "backfill_replay"
    output.mkdir(parents=True, exist_ok=True)
    (output / "contracts.jsonl").write_text(
        "".join(json.dumps(row.model_dump(mode="json"), sort_keys=True) + "\n" for row in contracts)
    )
    (output / "snapshot_ledger.jsonl").write_text(
        "".join(json.dumps(row.model_dump(mode="json"), sort_keys=True) + "\n" for row in records)
    )
    plan = build_replay_plan(records)
    (output / "replay_plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    status_counts: dict[str, int] = {}
    for row in records:
        status_counts[row.observation_status] = status_counts.get(row.observation_status, 0) + 1
    summary = {
        "schema_version": "historical-backfill-replay-summary-v1",
        "contract_count": len(contracts),
        "snapshot_count": len(records),
        "source_ids": sorted({row.source_id for row in records}),
        "status_counts": status_counts,
        "partition_count": len({row.partition_id for row in records}),
        "correction_count": sum(row.correction_sequence > 0 for row in records),
        "late_arrival_count": sum(row.late_arriving for row in records),
        "replay_eligible_count": plan["eligible_snapshot_count"],
        "replay_plan_sha256": plan["plan_sha256"],
        "raw_payload_policy": "ignored_local_immutable_snapshots_only",
        "publication_effect": "none",
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print({"summary": summary, "output": repo_relative(output)})


if __name__ == "__main__":
    main()

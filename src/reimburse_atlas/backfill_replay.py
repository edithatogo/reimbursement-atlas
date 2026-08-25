"""Deterministic backfill, immutable snapshot, and replay contracts."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from typing import Annotated, Literal, TypedDict

from pydantic import Field, model_validator

from reimburse_atlas.models import FrozenModel, NonEmptyStr

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
ObservationStatus = Literal["acquired", "failed", "metadata_only"]


class _StagedSnapshot(TypedDict):
    snapshot_id: str
    source_id: str
    source_version_id: str
    partition_id: str
    partition_value: str
    logical_asset_id: str
    source_url: str
    archive_period: str
    observation_status: ObservationStatus
    payload_sha256: str | None
    metadata_sha256: str
    idempotency_key: str
    rights_state: str


class BackfillReplayContract(FrozenModel):
    """Normative replay behavior for one source family."""

    contract_id: NonEmptyStr
    source_id: NonEmptyStr
    partition_identity: tuple[NonEmptyStr, ...]
    snapshot_identity: tuple[NonEmptyStr, ...]
    idempotency_rule: Literal["partition_and_snapshot_sha256"]
    late_arrival_rule: Literal["append_then_replay_partition"]
    correction_rule: Literal["new_snapshot_never_overwrite"]
    supersession_rule: Literal["explicit_acyclic_predecessor"]
    replay_order: tuple[NonEmptyStr, ...]
    deterministic_output_rule: Literal["canonical_json_sha256"]
    missing_payload_rule: Literal["metadata_only_fail_closed"]


class HistoricalSnapshotRecord(FrozenModel):
    """One immutable historical observation within a logical partition."""

    snapshot_id: Sha256
    source_id: NonEmptyStr
    source_version_id: NonEmptyStr
    partition_id: Sha256
    partition_value: NonEmptyStr
    logical_asset_id: NonEmptyStr
    source_url: NonEmptyStr
    archive_period: NonEmptyStr
    observation_status: ObservationStatus
    payload_sha256: Sha256 | None = None
    metadata_sha256: Sha256
    idempotency_key: Sha256
    correction_sequence: int = Field(ge=0)
    supersedes_snapshot_id: Sha256 | None = None
    late_arriving: bool
    replay_eligible: bool
    rights_state: NonEmptyStr

    @model_validator(mode="after")
    def validate_snapshot_state(self) -> HistoricalSnapshotRecord:
        """Require bytes for acquired snapshots and explicit predecessors for corrections."""
        if (self.observation_status == "acquired") != (self.payload_sha256 is not None):
            message = "only acquired snapshots may carry a payload checksum"
            raise ValueError(message)
        if (self.correction_sequence > 0) != (self.supersedes_snapshot_id is not None):
            message = "corrections require exactly one superseded snapshot"
            raise ValueError(message)
        if self.replay_eligible != (self.observation_status == "acquired"):
            message = "only checksum-bound acquired snapshots are replay eligible"
            raise ValueError(message)
        return self


def canonical_sha256(value: object) -> str:
    """Hash canonical JSON bytes."""
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def logical_asset_id(row: Mapping[str, object]) -> str:
    """Return a stable source-family asset identity independent of retrieval order."""
    return canonical_sha256({
        "source_id": row["source_id"],
        "source_url": row.get("source_url") or row.get("file_url"),
        "file_name": row.get("file_name", "unknown"),
    })


def build_snapshot_records(  # ruff:ignore[too-many-locals]
    rows: Iterable[Mapping[str, object]],
) -> tuple[HistoricalSnapshotRecord, ...]:
    """Build a deterministic ledger and explicit correction chains."""
    staged_by_id: dict[str, _StagedSnapshot] = {}
    for row in rows:
        source_id = str(row["source_id"])
        archive_period = str(row.get("archive_period", "unknown"))
        asset_id = logical_asset_id(row)
        partition_value = f"{source_id}/{archive_period}/{asset_id}"
        partition_id = canonical_sha256({"partition": partition_value})
        payload = row.get("checksum_sha256")
        payload_sha = payload if isinstance(payload, str) else None
        status = str(row.get("status", "planned"))
        observation_status: ObservationStatus = (
            "acquired"
            if status in {"cached", "downloaded"} and payload_sha is not None
            else "failed"
            if status == "download_failed"
            else "metadata_only"
        )
        metadata = {
            key: row.get(key)
            for key in (
                "source_id",
                "source_version_id",
                "source_url",
                "file_url",
                "file_name",
                "archive_period",
                "file_kind",
                "licence_gate",
                "status",
            )
        }
        metadata_sha = canonical_sha256(metadata)
        snapshot_id = canonical_sha256({
            "partition_id": partition_id,
            "payload_sha256": payload_sha,
            "metadata_sha256": metadata_sha,
        })
        staged: _StagedSnapshot = {
            "snapshot_id": snapshot_id,
            "source_id": source_id,
            "source_version_id": str(row["source_version_id"]),
            "partition_id": partition_id,
            "partition_value": partition_value,
            "logical_asset_id": asset_id,
            "source_url": str(row.get("source_url") or row.get("file_url")),
            "archive_period": archive_period,
            "observation_status": observation_status,
            "payload_sha256": payload_sha if observation_status == "acquired" else None,
            "metadata_sha256": metadata_sha,
            "idempotency_key": canonical_sha256({
                "partition_id": partition_id,
                "snapshot_id": snapshot_id,
            }),
            "rights_state": str(row.get("licence_gate", "public_reuse_review")),
        }
        staged_by_id.setdefault(snapshot_id, staged)

    records: list[HistoricalSnapshotRecord] = []
    by_partition: dict[str, list[_StagedSnapshot]] = {}
    for item in staged_by_id.values():
        by_partition.setdefault(str(item["partition_id"]), []).append(item)
    for partition_rows in by_partition.values():
        ordered = sorted(
            partition_rows,
            key=lambda item: (str(item["source_version_id"]), str(item["snapshot_id"])),
        )
        predecessor: str | None = None
        for sequence, item in enumerate(ordered):
            records.append(
                HistoricalSnapshotRecord(
                    **item,
                    correction_sequence=sequence,
                    supersedes_snapshot_id=predecessor,
                    late_arriving=sequence > 0,
                    replay_eligible=item["observation_status"] == "acquired",
                )
            )
            predecessor = str(item["snapshot_id"])
    return tuple(sorted(records, key=lambda item: (item.partition_id, item.correction_sequence)))


def build_replay_plan(records: Iterable[HistoricalSnapshotRecord]) -> dict[str, object]:
    """Build a deterministic, content-addressed replay plan."""
    ordered = sorted(
        (row for row in records if row.replay_eligible),
        key=lambda row: (row.partition_id, row.correction_sequence, row.snapshot_id),
    )
    steps = [
        {
            "ordinal": ordinal,
            "partition_id": row.partition_id,
            "snapshot_id": row.snapshot_id,
            "payload_sha256": row.payload_sha256,
            "idempotency_key": row.idempotency_key,
            "supersedes_snapshot_id": row.supersedes_snapshot_id,
        }
        for ordinal, row in enumerate(ordered, 1)
    ]
    return {
        "schema_version": "historical-replay-plan-v1",
        "deterministic": True,
        "eligible_snapshot_count": len(steps),
        "steps": steps,
        "plan_sha256": canonical_sha256(steps),
    }

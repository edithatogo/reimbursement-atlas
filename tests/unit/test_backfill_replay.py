"""Tests for immutable historical snapshots and deterministic replay."""

from __future__ import annotations

from reimburse_atlas.backfill_replay import build_replay_plan, build_snapshot_records


def _row(*, version: str, checksum: str | None, status: str = "downloaded") -> dict[str, object]:
    return {
        "source_id": "au_mbs",
        "source_version_id": version,
        "source_url": "https://www.mbsonline.gov.au/archive/items.csv",
        "file_name": "items.csv",
        "archive_period": "2025-07",
        "file_kind": "csv",
        "licence_gate": "public_reuse_review",
        "status": status,
        "checksum_sha256": checksum,
    }


def test_repeated_observation_is_idempotent() -> None:
    rows = build_snapshot_records([_row(version="v1", checksum="a" * 64)])
    repeated = build_snapshot_records([_row(version="v1", checksum="a" * 64)])
    assert rows == repeated
    assert build_replay_plan(rows) == build_replay_plan(repeated)
    assert (
        build_snapshot_records([
            _row(version="v1", checksum="a" * 64),
            _row(version="v1", checksum="a" * 64),
        ])
        == rows
    )


def test_correction_appends_and_supersedes_without_overwrite() -> None:
    rows = build_snapshot_records([
        _row(version="v1", checksum="a" * 64),
        _row(version="v2", checksum="b" * 64),
    ])
    assert rows[0].correction_sequence == 0
    assert rows[1].correction_sequence == 1
    assert rows[1].supersedes_snapshot_id == rows[0].snapshot_id
    assert rows[1].late_arriving is True
    assert rows[0].snapshot_id != rows[1].snapshot_id


def test_missing_or_failed_payloads_fail_closed() -> None:
    metadata = build_snapshot_records([_row(version="v1", checksum=None, status="planned")])[0]
    failed = build_snapshot_records([_row(version="v1", checksum=None, status="download_failed")])[
        0
    ]
    assert metadata.observation_status == "metadata_only"
    assert failed.observation_status == "failed"
    assert not metadata.replay_eligible
    assert not failed.replay_eligible


def test_replay_order_is_input_order_independent() -> None:
    first = _row(version="v1", checksum="a" * 64)
    second = _row(version="v2", checksum="b" * 64)
    assert build_replay_plan(build_snapshot_records([first, second])) == build_replay_plan(
        build_snapshot_records([second, first])
    )


def test_partition_identity_separates_periods() -> None:
    first = _row(version="v1", checksum="a" * 64)
    second = {**first, "source_version_id": "v2", "archive_period": "2026-01"}
    rows = build_snapshot_records([first, second])
    assert rows[0].partition_id != rows[1].partition_id
    assert all(row.correction_sequence == 0 for row in rows)

"""Tests for source snapshot provenance records."""

from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.contracts import SourceSnapshotRecord
from reimburse_atlas.registry import project_root
from reimburse_atlas.snapshots import build_fixture_snapshots, file_sha256


def test_file_sha256_is_stable_for_fixture() -> None:
    """A fixture checksum should be a 64-character lowercase SHA-256 digest."""
    digest = file_sha256(project_root() / "tests/fixtures/mbs_fragment.xml")
    assert len(digest) == 64
    assert digest == digest.lower()


def test_build_fixture_snapshots() -> None:
    """Committed parser fixtures should have explicit snapshot records."""
    records = build_fixture_snapshots()
    assert len(records) == 6
    assert {record.cache_scope for record in records} == {"public_derived_only"}
    assert all(record.checksum_sha256 for record in records)


def test_source_snapshot_seed_records_validate(repo_root: Path) -> None:
    """Source snapshot seed records should satisfy the contract."""
    path = repo_root / "data" / "seed" / "source_snapshots.jsonl"
    records = [
        SourceSnapshotRecord.model_validate(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 6
    assert {record.cache_scope for record in records} == {"public_derived_only"}

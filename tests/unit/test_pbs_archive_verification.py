"""Tests for independent PBS archive verification evidence."""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

from scripts import make_pbs_archive_verification as verification


def _ia_digest(payload: bytes) -> str:
    digest = hashlib.sha1(payload, usedforsecurity=False).digest()
    return base64.b32encode(digest).decode().rstrip("=")


def test_exact_archive_digest_match_requires_identical_local_bytes(tmp_path: Path) -> None:
    payload = b"%PDF-1.7 verified"
    cached = tmp_path / "source.pdf"
    cached.write_bytes(payload)
    target = {
        "id": "pbs-one",
        "file_url": "https://www.pbs.gov.au/archive/source.pdf?variant=3",
        "source_version_id": "pbs_one",
    }
    receipt = {
        "id": "pbs-one",
        "cache_path": str(cached),
        "checksum_sha256": hashlib.sha256(payload).hexdigest(),
        "status": "cached",
    }
    captures = [
        {
            "digest": _ia_digest(payload),
            "length": str(len(payload)),
            "mimetype": "application/pdf",
            "original": "https://www.pbs.gov.au/archive/source.pdf",
            "statuscode": "200",
            "timestamp": "20260101000000",
        }
    ]

    row = verification.build_verification_rows([target], [receipt], captures)[0]

    assert row["verification_status"] == "exact_digest_match"
    assert row["local_checksum_sha1_base32"] == _ia_digest(payload)
    assert row["archive_capture_count"] == 1


def test_indexed_or_catalogued_source_without_bytes_is_not_checksum_verified() -> None:
    target = {
        "id": "pbs-missing",
        "file_url": "https://www.pbs.gov.au/archive/missing.pdf?variant=3",
        "source_version_id": "pbs_missing",
    }
    receipt = {"id": "pbs-missing", "status": "download_failed", "checksum_sha256": None}

    row = verification.build_verification_rows([target], [receipt], [])[0]

    assert row["verification_status"] == "no_archive_capture"
    assert row["source_byte_verified"] is False
    assert row["publication_identity_observed"] is True


def test_previous_sha1_is_reused_when_raw_cache_is_absent(tmp_path: Path) -> None:
    target = {
        "id": "pbs-one",
        "file_url": "https://www.pbs.gov.au/archive/source.pdf?variant=3",
        "source_version_id": "pbs_one",
    }
    receipt = {
        "id": "pbs-one",
        "cache_path": "data/raw_live/missing.pdf",
        "checksum_sha256": "a" * 64,
        "status": "cached",
    }
    previous = tmp_path / "previous.jsonl"
    previous.write_text(
        json.dumps({
            "id": "pbs-one",
            "local_checksum_sha1_base32": "OLDARCHIVEDIGEST",
            "local_checksum_sha256": "a" * 64,
        })
        + "\n",
        encoding="utf-8",
    )

    rows = verification.build_verification_rows(
        [target], [receipt], [], previous_rows=verification.load_jsonl(previous)
    )

    assert rows[0]["local_checksum_sha1_base32"] == "OLDARCHIVEDIGEST"


def test_cdx_parser_rejects_malformed_rows() -> None:
    payload = [
        ["timestamp", "original", "statuscode", "mimetype", "digest", "length"],
        ["20260101000000", "https://www.pbs.gov.au/a.pdf", "200", "application/pdf", "ABC", "1"],
        ["short"],
    ]

    assert verification.parse_cdx_payload(payload) == [
        {
            "timestamp": "20260101000000",
            "original": "https://www.pbs.gov.au/a.pdf",
            "statuscode": "200",
            "mimetype": "application/pdf",
            "digest": "ABC",
            "length": "1",
        }
    ]


def test_archive_prefix_groups_monthly_paths_by_official_year() -> None:
    value = "https://www.pbs.gov.au/publication/schedule/2025/01/source.pdf?variant=3"

    assert verification.archive_prefix(value) == (
        "https://www.pbs.gov.au/publication/schedule/2025/"
    )

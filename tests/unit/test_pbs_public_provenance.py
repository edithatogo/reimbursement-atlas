"""Tests for rights-safe public PBS provenance projections."""

from __future__ import annotations

from scripts import make_pbs_public_provenance as provenance


def test_public_projection_omits_raw_cache_paths_and_failure_details() -> None:
    targets = [
        {
            "id": "one",
            "archive_page": "https://www.pbs.gov.au/archive",
            "archive_period": "2025-01-01",
            "file_name": "source.zip",
            "file_url": "https://www.pbs.gov.au/publication/schedule/2025/01/2025-01-01-xml.zip?variant=3",
            "licence_gate": "public_reuse_review",
            "source_version_id": "pbs_one",
            "structured_format": "xml_zip",
        }
    ]
    receipts = [
        {
            "id": "one",
            "byte_size": 10,
            "cache_path": "data/raw_live/secret/source.zip",
            "checksum_sha256": "a" * 64,
            "detail": "local diagnostic",
            "status": "cached",
        }
    ]

    row = provenance.project_rows(targets, receipts)[0]

    assert "cache_path" not in row
    assert "detail" not in row
    assert row["checksum_sha256"] == "a" * 64
    assert row["raw_payload_included"] is False
    assert row["raw_redistribution_status"] == "allowed_owner_attested_permission"


def test_projection_keeps_missing_payload_explicit() -> None:
    targets = [
        {
            "id": "missing",
            "archive_page": "https://www.pbs.gov.au/archive",
            "archive_period": "1987-12-01",
            "file_name": "missing.pdf",
            "file_url": "https://www.pbs.gov.au/missing.pdf?variant=3",
            "licence_gate": "public_reuse_review",
            "source_version_id": "pbs_missing",
        }
    ]
    receipts = [{"id": "missing", "status": "download_failed"}]

    row = provenance.project_rows(targets, receipts)[0]

    assert row["acquisition_status"] == "download_failed"
    assert row["checksum_sha256"] is None
    assert row["source_byte_verified"] is False

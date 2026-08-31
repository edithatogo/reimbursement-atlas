"""Tests for bounded local preservation of differing Internet Archive variants."""

from __future__ import annotations

import base64
import hashlib
import subprocess
from pathlib import Path

import pytest

from scripts import download_pbs_archive_variants as variants


def test_replay_url_uses_identity_modifier() -> None:
    assert variants.replay_url("20260101000000", "https://www.pbs.gov.au/archive/source.pdf") == (
        "https://web.archive.org/web/20260101000000id_/https://www.pbs.gov.au/archive/source.pdf"
    )


def test_download_rejects_non_pdf_archive_response(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        Path(command[command.index("--output") + 1]).write_bytes(b"<html>blocked</html>")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(variants.subprocess, "run", fake_run)

    status, _ = variants.download_variant(
        variants.replay_url("20260101000000", "https://www.pbs.gov.au/a.pdf"),
        tmp_path / "variant.pdf",
    )

    assert status == "invalid_content"


def test_download_fails_closed_when_curl_produces_no_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        variants.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0, "", ""),
    )

    status, detail = variants.download_variant(
        variants.replay_url("20260101000000", "https://www.pbs.gov.au/a.pdf"),
        tmp_path / "variant.pdf",
    )

    assert status == "download_failed"
    assert "without producing" in detail


def test_only_digest_mismatches_are_planned() -> None:
    verification_rows = [
        {
            "id": "one",
            "source_url": "https://www.pbs.gov.au/a.pdf",
            "verification_status": "exact_digest_match",
        },
        {
            "id": "two",
            "source_url": "https://www.pbs.gov.au/b.pdf",
            "verification_status": "digest_mismatch",
        },
    ]
    captures = [
        {
            "original": "https://www.pbs.gov.au/b.pdf",
            "timestamp": "20260101000000",
            "digest": "ABC",
        }
    ]

    planned = variants.plan_variants(verification_rows, captures)

    assert len(planned) == 1
    assert planned[0]["id"] == "two_20260101000000_ABC"
    assert planned[0]["raw_redistribution_status"] == "outside_pbs_permission_scope"


def test_http_capture_is_planned_for_https_mismatch() -> None:
    verification_rows = [
        {
            "id": "one",
            "source_url": "https://www.pbs.gov.au/a.pdf",
            "verification_status": "digest_mismatch",
        }
    ]
    captures = [
        {
            "original": "http://www.pbs.gov.au/a.pdf",
            "timestamp": "20260101000000",
            "digest": "ABC",
        }
    ]

    planned = variants.plan_variants(verification_rows, captures)

    assert len(planned) == 1
    assert planned[0]["official_source_url"] == "https://www.pbs.gov.au/a.pdf"
    assert "/http://www.pbs.gov.au/a.pdf" in planned[0]["archive_replay_url"]


def test_sha1_base32_matches_internet_archive_digest_encoding(tmp_path: Path) -> None:
    payload = b"%PDF-1.7 archived variant"
    path = tmp_path / "variant.pdf"
    path.write_bytes(payload)
    expected = (
        base64.b32encode(hashlib.sha1(payload, usedforsecurity=False).digest()).decode().rstrip("=")
    )

    assert variants.sha1_base32(path) == expected

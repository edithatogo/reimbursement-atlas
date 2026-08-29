"""Tests for official historical PBS publication discovery."""

import re
import subprocess
from pathlib import Path

import pytest

from scripts import discover_historical_pbs_archive as archive


def test_discovery_keeps_only_official_pdf_snapshots(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    links = [
        "https://www.pbs.gov.au/publication/schedule/2025/01/2025-01-01-general.pdf?variant=3",
        "https://www.pbs.gov.au/publication/schedule/2025/01/index.html",
        "https://example.com/not-official.pdf",
    ]

    def fake_links(_url: str) -> list[str]:
        return links

    monkeypatch.setattr(archive, "fetch_links", fake_links)
    rows = archive.discover(year=2003)
    assert len(rows) == 1
    assert rows[0]["file_url"] == links[0]
    assert rows[0]["source_id"] == "au_pbs"
    assert rows[0]["download_policy"] == "download_for_local_review"
    assert "structured API" in str(rows[0]["notes"])
    assert re.fullmatch(r"[a-z0-9_]+", str(rows[0]["source_version_id"]))


def test_pbs_host_is_accepted_by_hardened_downloader(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from scripts.download_historical_sources import download_payload

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        Path(command[command.index("--output") + 1]).write_bytes(b"%PDF-1.7")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("scripts.download_historical_sources.subprocess.run", fake_run)
    status, detail = download_payload(
        "https://www.pbs.gov.au/publication/schedule/example.pdf",
        tmp_path / "example.pdf",
        force=False,
        max_time_seconds=1,
    )
    assert status == "downloaded"
    assert detail == "Retrieved into ignored local cache."

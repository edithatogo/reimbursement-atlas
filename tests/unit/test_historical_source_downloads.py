"""Tests for bounded historical-source acquisition."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import download_historical_sources


def test_download_uses_configured_bounded_transfer_time(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Large official files can extend the bound without removing it."""
    observed: list[str] = []

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        observed.extend(command)
        Path(command[command.index("--output") + 1]).write_bytes(b"payload")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(download_historical_sources.subprocess, "run", fake_run)

    status, _ = download_historical_sources.download_payload(
        "https://www.mbsonline.gov.au/archive.pdf",
        tmp_path / "archive.pdf",
        force=False,
        max_time_seconds=180,
    )

    assert status == "downloaded"
    assert observed[observed.index("--max-time") + 1] == "180"
    assert observed[observed.index("--retry-max-time") + 1] == "180"


def test_download_rejects_untrusted_host_before_network(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A longer timeout never weakens official-host enforcement."""
    called = False

    def fake_run(*_: object, **__: object) -> subprocess.CompletedProcess[str]:
        nonlocal called
        called = True
        return subprocess.CompletedProcess([], 0, "", "")

    monkeypatch.setattr(download_historical_sources.subprocess, "run", fake_run)
    status, _ = download_historical_sources.download_payload(
        "https://example.com/archive.pdf",
        tmp_path / "archive.pdf",
        force=False,
        max_time_seconds=180,
    )

    assert status == "blocked_untrusted_host"
    assert called is False


def test_download_records_official_404_as_upstream_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A removed official snapshot is terminal evidence, not a transport outage."""

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.CalledProcessError(
            22, command, stderr="curl: (22) The requested URL returned error: 404"
        )

    monkeypatch.setattr(download_historical_sources.subprocess, "run", fake_run)
    status, detail = download_historical_sources.download_payload(
        "https://www.mbsonline.gov.au/removed.txt",
        tmp_path / "removed.txt",
        force=False,
        max_time_seconds=45,
    )

    assert status == "upstream_unavailable"
    assert "404" in detail


def test_force_preserves_changed_predecessor_snapshot(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A correction creates a new snapshot and never overwrites prior bytes."""
    destination = tmp_path / "archive.csv"
    destination.write_bytes(b"first")

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        Path(command[command.index("--output") + 1]).write_bytes(b"corrected")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(download_historical_sources.subprocess, "run", fake_run)
    status, _ = download_historical_sources.download_payload(
        "https://www.mbsonline.gov.au/archive.csv",
        destination,
        force=True,
        max_time_seconds=45,
    )

    predecessor = (
        tmp_path
        / ".snapshots/archive"
        / "a7937b64b8caa58f03721bb6bacf5c78cb235febe0e70b1b84cd99541461a08e.csv"
    )
    assert status == "downloaded"
    assert destination.read_bytes() == b"corrected"
    assert predecessor.read_bytes() == b"first"

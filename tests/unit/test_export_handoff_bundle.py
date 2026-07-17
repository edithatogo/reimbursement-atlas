"""Tests for the handoff package exporter."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scripts.export_handoff_bundle import export_handoff


def test_export_handoff_writes_redacted_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The exporter records basenames and verifies the generated bundle."""
    root = tmp_path / "repo"
    root.mkdir()
    readiness = root / "data" / "derived" / "release_readiness"
    readiness.mkdir(parents=True)
    (readiness / "summary.json").write_text(
        json.dumps({"repository_release_ready": True}), encoding="utf-8"
    )
    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        calls.append(command)
        if command[-2:] == ["rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(command, 0, "abc123\n", "")
        if "bundle" in command and "create" in command:
            Path(command[command.index("create") + 1]).write_bytes(b"bundle")
        elif "archive" in command:
            output = next(
                item.removeprefix("--output=") for item in command if item.startswith("--output=")
            )
            Path(output).write_bytes(b"archive")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("scripts.export_handoff_bundle.subprocess.run", fake_run)
    manifest = export_handoff(
        root=root,
        output_dir=tmp_path / "handoff",
        prefix="reimbursement-atlas-v-test",
        now=datetime(2026, 7, 17, tzinfo=UTC),
    )
    assert manifest["commit"] == "abc123"
    assert manifest["generated_at"] == "2026-07-17T00:00:00Z"
    assert manifest["bundle"]["path"] == "reimbursement-atlas-v-test.git.bundle"
    assert manifest["archive"]["path"] == "reimbursement-atlas-v-test.tar.gz"
    assert manifest["readiness"]["repository_release_ready"] is True
    assert any(
        str(tmp_path / "handoff" / "reimbursement-atlas-v-test.git.bundle") in call
        for call in calls
    )
    assert any(
        str(tmp_path / "handoff" / "reimbursement-atlas-v-test.tar.gz") in item
        for call in calls
        for item in call
    )
    assert "tmp_path" not in json.dumps(manifest)


def test_export_handoff_rejects_path_prefix(tmp_path: Path) -> None:
    """A prefix cannot escape the caller's output directory."""
    with pytest.raises(ValueError, match="filename stem"):
        export_handoff(root=tmp_path, output_dir=tmp_path, prefix="../unsafe")

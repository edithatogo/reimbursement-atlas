from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from reimburse_atlas.action_pins import (
    first_sha_from_ls_remote,
    resolve_action_pin,
    resolve_action_pins,
)
from reimburse_atlas.automation import WorkflowPinClass, WorkflowUseRecord


@dataclass(frozen=True)
class _Completed:
    returncode: int
    stdout: str = ""
    stderr: str = ""


def _workflow_use(uses: str, ref: str, pin_class: str) -> WorkflowUseRecord:
    action = uses.rsplit("@", 1)[0] if "@" in uses else uses
    return WorkflowUseRecord(
        workflow=".github/workflows/ci.yml",
        line=1,
        uses=uses,
        action=action,
        ref=ref,
        pin_class=cast("WorkflowPinClass", pin_class),
        is_official_github_action=action.startswith(("actions/", "github/")),
        policy_status="warn",
        policy_note="test",
    )


def test_first_sha_extracts_git_ls_remote_output() -> None:
    sha = "a" * 40
    assert first_sha_from_ls_remote(f"{sha}\trefs/tags/v1\n") == sha
    assert first_sha_from_ls_remote("not a sha\n") is None


def test_resolve_action_pin_skips_already_pinned() -> None:
    record = _workflow_use("actions/checkout@" + "a" * 40, "a" * 40, "sha")
    result = resolve_action_pin(record)
    assert result.status == "skipped_sha"
    assert result.suggested_uses is None


def test_resolve_action_pin_skips_local_or_docker() -> None:
    record = _workflow_use("./.github/actions/local", "", "local")
    result = resolve_action_pin(record)
    assert result.status == "skipped_local_or_docker"


def test_resolve_action_pin_success(monkeypatch) -> None:
    sha = "b" * 40

    def fake_run(*_args, **_kwargs):
        return _Completed(0, f"{sha}\trefs/tags/v1\n")

    monkeypatch.setattr(subprocess, "run", fake_run)
    record = _workflow_use("actions/checkout@v1", "v1", "major")
    result = resolve_action_pin(record)
    assert result.status == "resolved"
    assert result.suggested_uses == f"actions/checkout@{sha}"
    assert result.as_row()["resolved_sha"] == sha


def test_resolve_action_pin_continues_to_plain_ref(monkeypatch) -> None:
    sha = "c" * 40
    calls = []

    def fake_run(*args, **_kwargs):
        calls.append(args)
        if len(calls) == 1:
            return _Completed(2, "", "not found")
        return _Completed(0, f"{sha}\tHEAD\n")

    monkeypatch.setattr(subprocess, "run", fake_run)
    record = _workflow_use("owner/action@feature", "feature", "floating")
    result = resolve_action_pin(record)
    assert result.status == "resolved"
    assert len(calls) == 2


def test_resolve_action_pin_classifies_network_and_missing_tool(monkeypatch) -> None:
    def network_run(*_args, **_kwargs):
        return _Completed(128, "", "Could not resolve host: github.com")

    monkeypatch.setattr(subprocess, "run", network_run)
    record = _workflow_use("actions/checkout@v1", "v1", "major")
    assert resolve_action_pin(record).status == "blocked_network"

    def missing_run(*_args, **_kwargs):
        msg = "git"
        raise FileNotFoundError(msg)

    monkeypatch.setattr(subprocess, "run", missing_run)
    assert resolve_action_pin(record).status == "missing_tool"


def test_resolve_action_pin_classifies_timeout_and_failure(monkeypatch) -> None:
    def timeout_run(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd="git", timeout=1)

    monkeypatch.setattr(subprocess, "run", timeout_run)
    record = _workflow_use("actions/checkout@v1", "v1", "major")
    assert resolve_action_pin(record).status == "failed"

    def fail_run(*_args, **_kwargs):
        return _Completed(2, "", "not found")

    monkeypatch.setattr(subprocess, "run", fail_run)
    assert resolve_action_pin(record).status == "failed"
    assert resolve_action_pin(_workflow_use("owner/action", "", "unknown")).status == "failed"


def test_resolve_action_pins_cascades_network_block(monkeypatch, tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "ci.yml").write_text(
        """
name: CI
on: [push]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
""".strip()
        + "\n",
        encoding="utf-8",
    )
    calls = 0

    def network_run(*_args, **_kwargs):
        nonlocal calls
        calls += 1
        return _Completed(128, "", "Could not resolve host: github.com")

    monkeypatch.setattr(subprocess, "run", network_run)
    results = resolve_action_pins(tmp_path)
    assert [result.status for result in results] == ["blocked_network", "blocked_network"]
    assert calls == 1

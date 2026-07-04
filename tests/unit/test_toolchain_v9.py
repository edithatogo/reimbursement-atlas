"""Tests for external toolchain classification."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.toolchain import classify_gate_result, run_external_quality_gate


def test_wrong_pypi_pixi_is_not_marked_as_missing() -> None:
    stderr = "The database needs to be migrated. Run `pixi migrate`."

    assert classify_gate_result(1, "", stderr) == "wrong_tool"


def test_network_failure_classification_still_wins() -> None:
    stderr = "curl: (6) Could not resolve host: pixi.sh"

    assert classify_gate_result(6, "", stderr) == "blocked_network"


def test_run_external_quality_gate_passes(repo_root: Path) -> None:
    record = run_external_quality_gate(
        gate_id="python_version_probe",
        command=("python", "--version"),
        cwd=repo_root,
        timeout_seconds=30,
    )

    assert record.outcome == "passed"
    assert record.return_code == 0


def test_run_external_quality_gate_missing_tool(repo_root: Path) -> None:
    record = run_external_quality_gate(
        gate_id="missing_tool_probe",
        command=("definitely-not-a-real-reimburse-atlas-tool", "--version"),
        cwd=repo_root,
        timeout_seconds=30,
    )

    assert record.outcome == "missing_tool"
    assert record.return_code is None

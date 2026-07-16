"""Tests for external toolchain classification."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.toolchain import classify_gate_result, run_external_quality_gate
from scripts.make_fuzzy_prefilter_benchmark import build_benchmark
from scripts.make_mojo_parity_report import build_mojo_parity_report
from scripts.make_toolchain_report import cli_probe_row


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


def test_toolchain_cli_probe_redacts_machine_path() -> None:
    row = cli_probe_row("python", ("python", "--version"))

    assert row.available is True
    assert row.path == "PATH:python"
    assert "/" not in row.path


def test_mojo_parity_reference_contract_is_deterministic(repo_root: Path) -> None:
    """The Python reference remains testable when Mojo is unavailable."""
    report = build_mojo_parity_report(repo_root, run_smoke=False)

    assert report["python_reference_status"] == "pass"
    assert report["benchmark_contract"]["status"] == "pass"
    assert report["mojo_smoke"]["status"] == "not_run"
    assert report["benchmark_contract"]["deterministic"] is True
    assert len(report["benchmark_contract"]["workload_sha256"]) == 64
    assert report["benchmark_contract"]["fixed_width_output_tokens"] == 4
    assert (
        report["benchmark_contract"]
        == build_mojo_parity_report(repo_root, run_smoke=False)["benchmark_contract"]
    )


def test_fuzzy_prefilter_benchmark_records_recall_and_review_boundary(repo_root: Path) -> None:
    """Synthetic recall evidence must remain separate from evidence readiness."""
    report = build_benchmark(repo_root)

    assert report["python_reference_status"] == "pass"
    assert report["recall"] == 1.0
    assert report["reviewer_signoff_required"] is True
    assert report["status"] == "review_required"

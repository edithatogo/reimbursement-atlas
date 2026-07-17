from __future__ import annotations

from pathlib import Path

from reimburse_atlas.local_quality import (
    QualityGateSpec,
    default_quality_gate_specs,
    run_quality_gate,
    run_quality_gate_profile,
    specs_for_profile,
    summarise_quality_gate_run,
    write_quality_gate_run,
)


def test_default_quality_gate_profiles_include_core_checks() -> None:
    specs = default_quality_gate_specs(Path.cwd())
    ids = {spec.id for spec in specs}
    assert {"ruff_check", "pytest_coverage", "dashboard_build", "pip_audit_strict"} <= ids
    ci_ids = {spec.id for spec in specs_for_profile("ci", root=Path.cwd())}
    assert "pip_audit_strict" not in ci_ids
    assert "dashboard_build" in ci_ids


def test_quality_gate_dry_run_is_skipped(tmp_path: Path) -> None:
    spec = QualityGateSpec(
        id="dry_run_gate",
        category="test",
        command=("python", "-c", "raise SystemExit(1)"),
        cwd=".",
        profiles=("quick",),
    )
    record = run_quality_gate(spec, root=tmp_path, dry_run=True)
    assert record.status == "skipped"
    assert record.return_code is None
    assert record.cwd == "."


def test_quality_gate_classifies_success_and_failure(tmp_path: Path) -> None:
    success = QualityGateSpec(
        id="success",
        category="test",
        command=("python", "-c", "print('ok')"),
        cwd=".",
        profiles=("quick",),
    )
    failure = QualityGateSpec(
        id="failure",
        category="test",
        command=(
            "python",
            "-c",
            "import sys; print('diagnostic', file=sys.stderr); raise SystemExit(3)",
        ),
        cwd=".",
        profiles=("quick",),
    )
    assert run_quality_gate(success, root=tmp_path).status == "passed"
    assert run_quality_gate(success, root=tmp_path).stdout_excerpt == ""
    failed = run_quality_gate(failure, root=tmp_path)
    assert failed.status == "failed"
    assert failed.return_code == 3
    assert failed.cwd == "."
    assert failed.stderr_excerpt == "diagnostic"


def test_quality_gate_summary_tracks_blocking_failures() -> None:
    records, summary = run_quality_gate_profile("quick", dry_run=True)
    assert records
    assert summary.skipped == len(records)
    assert summary.blocking_failures == len(records)
    assert not summary.release_ready
    overridden = summarise_quality_gate_run([], profile="quick")
    assert overridden.release_ready


def test_quality_gate_as_rows_and_write(tmp_path: Path) -> None:
    spec = QualityGateSpec(
        id="row_gate",
        category="test",
        command=("python", "-c", "print('ok')"),
        profiles=("quick",),
    )
    record = run_quality_gate(spec, root=tmp_path)
    summary = summarise_quality_gate_run([record], profile="quick")
    paths = write_quality_gate_run([record], summary, output_dir=tmp_path / "quality")
    assert spec.as_row()["profiles"] == "quick"
    assert record.as_row()["status"] == "passed"
    assert summary.as_row()["release_ready"] is True
    assert all(path.exists() for path in paths)


def test_quality_gate_classifies_missing_tool_and_timeout(tmp_path: Path) -> None:
    missing = QualityGateSpec(
        id="missing",
        category="test",
        command=("definitely-not-a-real-executable-xyz",),
        profiles=("quick",),
    )
    assert run_quality_gate(missing, root=tmp_path).status == "missing_tool"

    timeout = QualityGateSpec(
        id="timeout",
        category="test",
        command=("python", "-c", "import time; time.sleep(1)"),
        timeout_seconds=0,
        profiles=("quick",),
    )
    assert run_quality_gate(timeout, root=tmp_path).status == "timed_out"


def test_quality_gate_profile_executes_custom_dry_run() -> None:
    records, summary = run_quality_gate_profile("nightly", dry_run=True)
    assert records
    assert summary.gate_count == len(records)
    assert summary.skipped == len(records)

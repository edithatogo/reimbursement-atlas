"""Local quality-gate orchestration for CI/CD parity.

The module intentionally keeps the gate list data-driven and serialisable so the
same definitions can be used by local developers, GitHub Actions and Conductor
handoffs.  It does not replace GitHub-native checks; it records exactly which
checks passed, failed, timed out or were blocked by the active runtime.
"""

from __future__ import annotations

import json
import os
import subprocess  # nosec B404
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.registry import project_root, repo_relative, stable_generated_at
from reimburse_atlas.toolchain import classify_gate_result

QualityGateStatus = Literal[
    "passed",
    "failed",
    "blocked_network",
    "missing_tool",
    "timed_out",
    "wrong_tool",
    "skipped",
]
QualityGateProfile = Literal["quick", "ci", "release", "nightly"]
GateCategory = Literal[
    "format",
    "lint",
    "typecheck",
    "test",
    "security",
    "build",
    "data",
    "dashboard",
    "supply_chain",
    "architecture",
    "mutation",
]


@dataclass(frozen=True)
class QualityGateSpec:
    """One executable local quality gate."""

    id: str
    category: GateCategory
    command: tuple[str, ...]
    cwd: str = "."
    timeout_seconds: int = 300
    blocking: bool = True
    profiles: tuple[QualityGateProfile, ...] = ("ci", "release")
    notes: str = ""

    def as_row(self) -> dict[str, object]:
        """Return a JSON/CSV-safe representation."""
        return {
            **asdict(self),
            "command": " ".join(self.command),
            "profiles": ";".join(self.profiles),
        }


@dataclass(frozen=True)
class QualityGateRunRecord:
    """Result from one local quality-gate execution."""

    id: str
    category: GateCategory
    command: str
    cwd: str
    status: QualityGateStatus
    return_code: int | None
    duration_seconds: float
    blocking: bool
    generated_at: str
    stdout_excerpt: str
    stderr_excerpt: str
    notes: str

    def as_row(self) -> dict[str, object]:
        """Return a JSON/CSV-safe representation."""
        return asdict(self)


@dataclass(frozen=True)
class QualityGateRunSummary:
    """Summary of a quality-gate run."""

    schema_version: str
    profile: QualityGateProfile
    generated_at: str
    gate_count: int
    passed: int
    failed: int
    blocked_network: int
    missing_tool: int
    timed_out: int
    wrong_tool: int
    skipped: int
    blocking_failures: int
    release_ready: bool

    def as_row(self) -> dict[str, object]:
        """Return a JSON/CSV-safe representation."""
        return asdict(self)


def default_quality_gate_specs(root: Path | None = None) -> list[QualityGateSpec]:
    """Return the canonical local quality-gate matrix."""
    repo = root or project_root()
    dashboard_dir = repo / "apps" / "dashboard"
    python_prefix = ("uv", "run", "--all-extras")
    return [
        QualityGateSpec(
            id="ruff_check",
            category="lint",
            command=(*python_prefix, "ruff", "check", "."),
            timeout_seconds=180,
            profiles=("quick", "ci", "release"),
        ),
        QualityGateSpec(
            id="ruff_format_check",
            category="format",
            command=(*python_prefix, "ruff", "format", "--check", "."),
            timeout_seconds=180,
            profiles=("quick", "ci", "release"),
        ),
        QualityGateSpec(
            id="basedpyright",
            category="typecheck",
            command=(*python_prefix, "basedpyright"),
            timeout_seconds=240,
            profiles=("ci", "release"),
        ),
        QualityGateSpec(
            id="pytest_coverage",
            category="test",
            command=(
                *python_prefix,
                "pytest",
                "--cov=src/reimburse_atlas",
                "--cov-report=term-missing",
                "--cov-report=xml",
                "--cov-fail-under=90",
                "-q",
            ),
            timeout_seconds=600,
            profiles=("ci", "release"),
        ),
        QualityGateSpec(
            id="bandit",
            category="security",
            command=(
                *python_prefix,
                "bandit",
                "-q",
                "-c",
                "pyproject.toml",
                "-r",
                "src",
                "scripts",
            ),
            timeout_seconds=240,
            profiles=("ci", "release"),
        ),
        QualityGateSpec(
            id="compileall",
            category="build",
            command=(*python_prefix, "python", "-m", "compileall", "-q", "src", "scripts", "tests"),
            timeout_seconds=240,
            profiles=("quick", "ci", "release"),
        ),
        QualityGateSpec(
            id="seed_sync",
            category="data",
            command=(*python_prefix, "python", "scripts/validate_seed_sync.py"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
        ),
        QualityGateSpec(
            id="public_data_policy",
            category="data",
            command=(*python_prefix, "python", "scripts/check_public_data_policy.py"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
        ),
        QualityGateSpec(
            id="cli_validate",
            category="data",
            command=(*python_prefix, "python", "-m", "reimburse_atlas.cli", "validate"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
        ),
        QualityGateSpec(
            id="protocol_status",
            category="data",
            command=(*python_prefix, "python", "scripts/make_protocol_status.py"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
            notes="OSF/research protocol completeness evidence must regenerate cleanly.",
        ),
        QualityGateSpec(
            id="source_content_validation",
            category="data",
            command=(*python_prefix, "python", "scripts/make_source_validation.py"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
            notes=(
                "Downloaded source files must be validated or explicitly skipped by licence gates."
            ),
        ),
        QualityGateSpec(
            id="source_contracts",
            category="data",
            command=(*python_prefix, "python", "scripts/make_source_contracts.py"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
            notes="Source-specific contracts must regenerate before reviewed-source bundles.",
        ),
        QualityGateSpec(
            id="github_project_export",
            category="supply_chain",
            command=(*python_prefix, "python", "scripts/make_github_project_export.py"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
            notes="Generated GitHub Project import rows must stay in sync with issue drafts.",
        ),
        QualityGateSpec(
            id="final_handoff",
            category="data",
            command=(*python_prefix, "python", "scripts/make_final_handoff.py"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
            notes="Final environment-dependent handoff checklist must regenerate cleanly.",
        ),
        QualityGateSpec(
            id="roadmap_linkages",
            category="data",
            command=(*python_prefix, "python", "scripts/make_roadmap_linkages.py"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
            notes="Research questions must link to datasets, mappings and output plans.",
        ),
        QualityGateSpec(
            id="data_quality",
            category="data",
            command=(*python_prefix, "python", "scripts/make_data_quality_report.py"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
            notes="Seed and derived table quality checks must regenerate cleanly.",
        ),
        QualityGateSpec(
            id="data_dictionary",
            category="data",
            command=(*python_prefix, "python", "scripts/make_data_dictionary.py"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
            notes="Public candidate artefacts must have generated data-dictionary entries.",
        ),
        QualityGateSpec(
            id="licence_review_queue",
            category="data",
            command=(*python_prefix, "python", "scripts/make_licence_review_queue.py"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
            notes="Candidate artefacts must have checksum-bound human licence review rows.",
        ),
        QualityGateSpec(
            id="evidence_readiness",
            category="data",
            command=(*python_prefix, "python", "scripts/make_evidence_readiness.py"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
            notes="Protocolled research questions must have generated evidence-readiness rows.",
        ),
        QualityGateSpec(
            id="source_drift",
            category="data",
            command=(*python_prefix, "python", "scripts/make_source_drift_report.py"),
            timeout_seconds=120,
            profiles=("quick", "ci", "release"),
            notes="CSV/JSONL mirror and schema drift checks must regenerate cleanly.",
        ),
        QualityGateSpec(
            id="repo_automation_matrix",
            category="supply_chain",
            command=(*python_prefix, "python", "scripts/make_repo_automation_matrix.py"),
            timeout_seconds=120,
            profiles=("ci", "release"),
        ),
        QualityGateSpec(
            id="architecture_report",
            category="architecture",
            command=(*python_prefix, "python", "scripts/make_architecture_report.py"),
            timeout_seconds=120,
            profiles=("ci", "release"),
        ),
        QualityGateSpec(
            id="sbom_generation",
            category="supply_chain",
            command=(*python_prefix, "python", "scripts/make_sbom.py"),
            timeout_seconds=180,
            profiles=("ci", "release"),
        ),
        QualityGateSpec(
            id="uv_build",
            category="build",
            command=("uv", "build"),
            timeout_seconds=240,
            profiles=("ci", "release"),
        ),
        QualityGateSpec(
            id="npm_ci_dashboard",
            category="dashboard",
            command=("npm", "ci"),
            cwd=str(dashboard_dir.relative_to(repo)),
            timeout_seconds=300,
            profiles=("ci", "release"),
        ),
        QualityGateSpec(
            id="npm_audit_dashboard",
            category="security",
            command=("npm", "audit", "--omit=dev", "--audit-level=moderate"),
            cwd=str(dashboard_dir.relative_to(repo)),
            timeout_seconds=180,
            profiles=("ci", "release"),
        ),
        QualityGateSpec(
            id="dashboard_build",
            category="dashboard",
            command=("npm", "run", "build"),
            cwd=str(dashboard_dir.relative_to(repo)),
            timeout_seconds=360,
            profiles=("ci", "release"),
        ),
        QualityGateSpec(
            id="pip_audit_strict",
            category="security",
            command=(*python_prefix, "pip-audit", "--strict"),
            timeout_seconds=240,
            blocking=False,
            profiles=("release",),
            notes="Network-backed advisory lookup may be blocked in sandboxes.",
        ),
        QualityGateSpec(
            id="zizmor_workflow_security",
            category="supply_chain",
            command=("uv", "tool", "run", "zizmor", "--min-severity", "medium", ".github"),
            timeout_seconds=240,
            blocking=False,
            profiles=("release",),
            notes="Advisory until action SHA pinning is complete.",
        ),
        QualityGateSpec(
            id="mutmut_unit_nightly",
            category="mutation",
            command=(*python_prefix, "mutmut", "run", "--max-children", "2"),
            timeout_seconds=3600,
            blocking=False,
            profiles=("nightly",),
            notes="Long-running mutation trend gate; not a PR blocker.",
        ),
    ]


def specs_for_profile(
    profile: QualityGateProfile,
    *,
    root: Path | None = None,
) -> list[QualityGateSpec]:
    """Return gates included in a quality-gate profile."""
    return [spec for spec in default_quality_gate_specs(root) if profile in spec.profiles]


def run_quality_gate(
    spec: QualityGateSpec,
    *,
    root: Path | None = None,
    dry_run: bool = False,
) -> QualityGateRunRecord:
    """Run one quality gate and return a structured result."""
    repo = root or project_root()
    cwd = (repo / spec.cwd).resolve()
    generated_at = stable_generated_at()
    command_text = " ".join(spec.command)
    if dry_run:
        return QualityGateRunRecord(
            id=spec.id,
            category=spec.category,
            command=command_text,
            cwd=repo_relative(cwd, repo),
            status="skipped",
            return_code=None,
            duration_seconds=0.0,
            blocking=spec.blocking,
            generated_at=generated_at,
            stdout_excerpt="",
            stderr_excerpt="",
            notes="Dry-run mode; command was not executed.",
        )
    env = {**os.environ, "PYTHONPATH": str(repo / "src")}
    try:
        completed = subprocess.run(  # nosec B603
            spec.command,
            cwd=cwd,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=spec.timeout_seconds,
        )
    except FileNotFoundError as exc:
        return _run_record(
            spec,
            command_text,
            cwd,
            repo,
            status="missing_tool",
            return_code=None,
            generated_at=generated_at,
            stdout="",
            stderr=str(exc),
            notes="Executable is unavailable in the active runtime.",
        )
    except subprocess.TimeoutExpired as exc:
        return _run_record(
            spec,
            command_text,
            cwd,
            repo,
            status="timed_out",
            return_code=None,
            generated_at=generated_at,
            stdout=exc.stdout if isinstance(exc.stdout, str) else "",
            stderr=exc.stderr if isinstance(exc.stderr, str) else "",
            notes="Command exceeded the configured timeout.",
        )
    status = classify_gate_result(completed.returncode, completed.stdout, completed.stderr)
    return _run_record(
        spec,
        command_text,
        cwd,
        repo,
        status=status,
        return_code=completed.returncode,
        generated_at=generated_at,
        stdout=completed.stdout,
        stderr=completed.stderr,
        notes=spec.notes or _notes_for_status(status),
    )


def run_quality_gate_profile(
    profile: QualityGateProfile,
    *,
    root: Path | None = None,
    dry_run: bool = False,
) -> tuple[list[QualityGateRunRecord], QualityGateRunSummary]:
    """Run all gates for a profile and return rows plus a summary."""
    records = [
        run_quality_gate(spec, root=root, dry_run=dry_run)
        for spec in specs_for_profile(profile, root=root)
    ]
    summary = summarise_quality_gate_run(records, profile=profile)
    return records, summary


def summarise_quality_gate_run(
    records: list[QualityGateRunRecord],
    *,
    profile: QualityGateProfile,
) -> QualityGateRunSummary:
    """Summarise gate outcomes and release-readiness."""
    counts: dict[QualityGateStatus, int] = {
        "passed": 0,
        "failed": 0,
        "blocked_network": 0,
        "missing_tool": 0,
        "timed_out": 0,
        "wrong_tool": 0,
        "skipped": 0,
    }
    for record in records:
        counts[record.status] += 1
    blocking_failures = sum(
        1 for record in records if record.blocking and record.status != "passed"
    )
    return QualityGateRunSummary(
        schema_version="local-quality-gates-v1",
        profile=profile,
        generated_at=stable_generated_at(),
        gate_count=len(records),
        passed=counts["passed"],
        failed=counts["failed"],
        blocked_network=counts["blocked_network"],
        missing_tool=counts["missing_tool"],
        timed_out=counts["timed_out"],
        wrong_tool=counts["wrong_tool"],
        skipped=counts["skipped"],
        blocking_failures=blocking_failures,
        release_ready=blocking_failures == 0,
    )


def write_quality_gate_run(
    records: list[QualityGateRunRecord],
    summary: QualityGateRunSummary,
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path, Path, Path]:
    """Write quality-gate run artefacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [record.as_row() for record in records]
    specs = [spec.as_row() for spec in default_quality_gate_specs()]
    jsonl_path = write_jsonl(rows, output_dir / "local_quality_gates.jsonl")
    csv_path = write_csv(rows, output_dir / "local_quality_gates.csv")
    spec_jsonl_path = write_jsonl(specs, output_dir / "local_quality_gate_specs.jsonl")
    spec_csv_path = write_csv(specs, output_dir / "local_quality_gate_specs.csv")
    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary.as_row(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return jsonl_path, csv_path, spec_jsonl_path, spec_csv_path, summary_path


def _run_record(
    spec: QualityGateSpec,
    command_text: str,
    cwd: Path,
    repo: Path,
    *,
    status: QualityGateStatus,
    return_code: int | None,
    generated_at: str,
    stdout: str,
    stderr: str,
    notes: str,
) -> QualityGateRunRecord:
    # Successful command output is machine-dependent (counts, timings and tool banners). Keep
    # diagnostics for non-passing gates, while making committed pass evidence byte-stable.
    stable_stdout = stdout if status != "passed" else ""
    stable_stderr = stderr if status != "passed" else ""
    return QualityGateRunRecord(
        id=spec.id,
        category=spec.category,
        command=command_text,
        cwd=repo_relative(cwd, repo),
        status=status,
        return_code=return_code,
        # Wall-clock duration is machine-dependent and would make generated
        # evidence fail the repository's deterministic-regeneration gate.
        duration_seconds=0.0,
        blocking=spec.blocking,
        generated_at=generated_at,
        stdout_excerpt=_excerpt(stable_stdout, repo=repo),
        stderr_excerpt=_excerpt(stable_stderr, repo=repo),
        notes=notes,
    )


def _excerpt(value: str, *, repo: Path, limit: int = 1_000) -> str:
    cleaned = " ".join(value.split())
    cleaned = cleaned.replace(str(repo), "<repo>")
    cleaned = cleaned.replace(str(Path.home()), "<home>")
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 1]}…"


def _notes_for_status(status: QualityGateStatus) -> str:
    notes = {
        "passed": "Gate passed in the active runtime.",
        "failed": "Gate returned a non-zero exit code.",
        "blocked_network": "Gate is installed but a required network service was unreachable.",
        "missing_tool": "Gate could not start because an executable is missing.",
        "timed_out": "Gate did not complete before the configured timeout.",
        "wrong_tool": "A same-named executable exists but is not the expected tool.",
        "skipped": "Gate was intentionally skipped.",
    }
    return notes[status]

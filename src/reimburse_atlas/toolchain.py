"""External quality-gate execution and classification utilities."""

from __future__ import annotations

import csv
import json
import subprocess  # nosec B404
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from reimburse_atlas.registry import project_root, repo_relative, stable_generated_at

GateOutcome = Literal[
    "passed",
    "failed",
    "blocked_network",
    "missing_tool",
    "timed_out",
    "wrong_tool",
]

NETWORK_MARKERS = (
    "temporary failure in name resolution",
    "could not resolve host",
    "failed to resolve",
    "nameresolutionerror",
)
MISSING_TOOL_MARKERS = (
    "no such file or directory",
    "command not found",
    "not found on path",
)
WRONG_TOOL_MARKERS = (
    "the database needs to be migrated",
    "run `pixi migrate`",
    "pixiv-api",
)


@dataclass(frozen=True)
class ExternalQualityGateRecord:
    """One attempted external quality/security gate."""

    id: str
    command: str
    cwd: str
    outcome: GateOutcome
    return_code: int | None
    generated_at: str
    stdout_excerpt: str
    stderr_excerpt: str
    notes: str

    def as_row(self) -> dict[str, object]:
        """Return a JSON/CSV-safe row."""
        return asdict(self)


def classify_gate_result(return_code: int, stdout: str, stderr: str) -> GateOutcome:
    """Classify a completed gate command."""
    if return_code == 0:
        return "passed"
    combined = f"{stdout}\n{stderr}".lower()
    if any(marker in combined for marker in NETWORK_MARKERS):
        return "blocked_network"
    if any(marker in combined for marker in WRONG_TOOL_MARKERS):
        return "wrong_tool"
    if return_code == 127 or any(marker in combined for marker in MISSING_TOOL_MARKERS):
        return "missing_tool"
    return "failed"


def run_external_quality_gate(
    *,
    gate_id: str,
    command: tuple[str, ...],
    cwd: Path,
    timeout_seconds: int = 180,
) -> ExternalQualityGateRecord:
    """Run and classify one external quality gate."""
    generated_at = stable_generated_at()
    command_text = " ".join(command)
    try:
        completed = subprocess.run(  # nosec B603
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except FileNotFoundError as exc:
        return ExternalQualityGateRecord(
            id=gate_id,
            command=command_text,
            cwd=repo_relative(cwd),
            outcome="missing_tool",
            return_code=None,
            generated_at=generated_at,
            stdout_excerpt="",
            stderr_excerpt=_excerpt(str(exc)),
            notes="Executable is not available in this runtime.",
        )
    except subprocess.TimeoutExpired as exc:
        return ExternalQualityGateRecord(
            id=gate_id,
            command=command_text,
            cwd=repo_relative(cwd),
            outcome="timed_out",
            return_code=None,
            generated_at=generated_at,
            stdout_excerpt=_excerpt(exc.stdout if isinstance(exc.stdout, str) else ""),
            stderr_excerpt=_excerpt(exc.stderr if isinstance(exc.stderr, str) else ""),
            notes="Command exceeded the configured timeout.",
        )

    outcome = classify_gate_result(completed.returncode, completed.stdout, completed.stderr)
    return ExternalQualityGateRecord(
        id=gate_id,
        command=command_text,
        cwd=repo_relative(cwd),
        outcome=outcome,
        return_code=completed.returncode,
        generated_at=generated_at,
        stdout_excerpt=_excerpt(completed.stdout),
        stderr_excerpt=_excerpt(completed.stderr),
        notes=_notes_for_outcome(outcome),
    )


def write_external_quality_gate_records(
    records: list[ExternalQualityGateRecord],
    *,
    json_path: Path,
    csv_path: Path,
) -> tuple[Path, Path]:
    """Write external quality-gate records as JSON and CSV."""
    json_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "external-quality-gates-v1",
        "records": [record.as_row() for record in records],
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "command",
                "cwd",
                "outcome",
                "return_code",
                "generated_at",
                "stdout_excerpt",
                "stderr_excerpt",
                "notes",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(record.as_row() for record in records)
    return json_path, csv_path


def _excerpt(value: str, limit: int = 800) -> str:
    cleaned = " ".join(value.split())
    cleaned = cleaned.replace(str(project_root()), "<repo>")
    cleaned = cleaned.replace(str(Path.home()), "<home>")
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 1]}…"


def _notes_for_outcome(outcome: GateOutcome) -> str:
    notes = {
        "passed": "Gate passed in the active runtime.",
        "failed": "Gate executed but returned a non-zero status; inspect logs before release.",
        "blocked_network": (
            "Gate is installed but could not reach its external advisory/network service."
        ),
        "missing_tool": (
            "Gate could not start because the executable is unavailable in this runtime."
        ),
        "timed_out": "Gate did not finish inside the configured timeout.",
        "wrong_tool": "A same-named executable exists but is not the expected official tool.",
    }
    return notes[outcome]

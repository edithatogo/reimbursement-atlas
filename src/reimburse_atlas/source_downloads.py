"""Cautious curl/wget/httpx acquisition helpers for public source files."""

from __future__ import annotations

import hashlib
import re

# Used only with shell=False and fixed curl/wget command construction.
import subprocess  # nosec B404
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import DataAcquisitionAttemptRecord, SourceFileRecord

DownloadStatus = Literal[
    "downloaded", "blocked_network", "failed", "skipped_licence_gate", "not_attempted"
]

NETWORK_ERROR_MARKERS = (
    "could not resolve host",
    "failed to lookup address information",
    "temporary failure in name resolution",
    "connection timed out",
    "couldn't connect",
    "failed to connect",
)


@dataclass(frozen=True)
class SourceDownloadPlan:
    """Local-only acquisition plan for one source-file record."""

    source_file_id: str
    method: str
    command: str
    target_path: str
    licence_gate: str
    should_execute: bool
    notes: str

    def as_row(self) -> dict[str, object]:
        """Return a JSON-serialisable row."""
        return asdict(self)


def safe_local_target(record: SourceFileRecord, output_dir: Path) -> Path:
    """Return the ignored local raw target path for a source file."""
    source_dir = output_dir / record.source_id
    file_name = record.file_name or f"{record.id}.{record.expected_format}"
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", file_name).strip("_")
    return source_dir / (safe_name or f"{record.id}.raw")


def build_download_plan(
    record: SourceFileRecord,
    *,
    output_dir: Path = Path("data/raw_live"),
    preferred_method: str = "curl",
) -> SourceDownloadPlan:
    """Build a shell acquisition plan without executing it."""
    target = safe_local_target(record, output_dir)
    executable = record.acquisition_mode in {"manual_download", "api_rate_limited"}
    if record.licence_gate in {"restricted_or_licence_review", "metadata_only"}:
        executable = False
    if record.file_role in {"landing_page", "licence_gate"}:
        executable = False
    if preferred_method == "wget":
        command = f"mkdir -p {target.parent} && wget -O {target} {record.source_url}"
    else:
        command = (
            f"mkdir -p {target.parent} && curl -L --fail --retry 3 -o {target} {record.source_url}"
        )
    return SourceDownloadPlan(
        source_file_id=record.id,
        method=preferred_method,
        command=command,
        target_path=str(target),
        licence_gate=record.licence_gate,
        should_execute=executable,
        notes=(
            "Executable local raw download candidate."
            if executable
            else "Metadata-only, landing-page or licence-gated record; do not auto-download."
        ),
    )


def _sha_slug(value: str, *, length: int = 10) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def _classify_failure(stderr: str) -> DownloadStatus:
    lowered = stderr.lower()
    if any(marker in lowered for marker in NETWORK_ERROR_MARKERS):
        return "blocked_network"
    return "failed"


def attempt_download(
    record: SourceFileRecord,
    *,
    output_dir: Path = Path("data/raw_live"),
    preferred_method: str = "curl",
    timeout_seconds: int = 60,
) -> DataAcquisitionAttemptRecord:
    """Attempt a local raw download with curl/wget, respecting licence gates."""
    plan = build_download_plan(record, output_dir=output_dir, preferred_method=preferred_method)
    attempted_at = datetime.now(UTC).isoformat()
    target_path = Path(plan.target_path)
    attempt_id = f"attempt_{record.id}_{_sha_slug(attempted_at)}"
    if not plan.should_execute:
        return DataAcquisitionAttemptRecord(
            id=attempt_id,
            source_file_id=record.id,
            attempted_at=attempted_at,
            method="curl" if preferred_method != "wget" else "wget",
            target_path=plan.target_path,
            status="skipped_licence_gate",
            exit_code=None,
            bytes_downloaded=0,
            command=plan.command,
            error_summary=plan.notes,
        )

    target_path.parent.mkdir(parents=True, exist_ok=True)
    args = (
        [
            "wget",
            "-O",
            str(target_path),
            str(record.source_url),
        ]
        if preferred_method == "wget"
        else [
            "curl",
            "-L",
            "--fail",
            "--retry",
            "2",
            "--connect-timeout",
            "10",
            "--max-time",
            str(timeout_seconds),
            "-o",
            str(target_path),
            str(record.source_url),
        ]
    )
    # Fixed curl/wget argv; no shell expansion is used.
    completed = subprocess.run(  # nosec B603
        args,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds + 15,
    )
    bytes_downloaded = target_path.stat().st_size if target_path.exists() else 0
    if completed.returncode == 0 and bytes_downloaded > 0:
        status: DownloadStatus = "downloaded"
        error_summary = "Downloaded to ignored local raw storage."
    else:
        status = _classify_failure(completed.stderr + completed.stdout)
        error_summary = (completed.stderr or completed.stdout or "Download command failed.").strip()
        if target_path.exists() and bytes_downloaded == 0:
            target_path.unlink()
    return DataAcquisitionAttemptRecord(
        id=attempt_id,
        source_file_id=record.id,
        attempted_at=attempted_at,
        method="curl" if preferred_method != "wget" else "wget",
        target_path=plan.target_path,
        status=status,
        exit_code=completed.returncode,
        bytes_downloaded=bytes_downloaded,
        command=" ".join(args),
        error_summary=error_summary[:500],
    )


def write_download_outputs(
    plans: list[SourceDownloadPlan],
    attempts: list[DataAcquisitionAttemptRecord],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path, Path]:
    """Write acquisition plans and attempt records."""
    output_dir.mkdir(parents=True, exist_ok=True)
    plan_rows = [plan.as_row() for plan in plans]
    attempt_rows = [attempt.model_dump(mode="json") for attempt in attempts]
    plan_jsonl = write_jsonl(plan_rows, output_dir / "download_plans.jsonl")
    plan_csv = write_csv(plan_rows, output_dir / "download_plans.csv")
    attempt_jsonl = write_jsonl(attempt_rows, output_dir / "download_attempts.jsonl")
    attempt_csv = write_csv(attempt_rows, output_dir / "download_attempts.csv")
    shell_path = output_dir / "download_commands.sh"
    shell_path.write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\n\n"
        + "\n".join(plan.command for plan in plans if plan.should_execute)
        + "\n",
        encoding="utf-8",
    )
    shell_path.chmod(0o755)
    return plan_jsonl, plan_csv, attempt_jsonl, attempt_csv

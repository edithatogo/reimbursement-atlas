"""Cautious curl/wget/httpx acquisition helpers for public source files."""

from __future__ import annotations

import hashlib
import re
import shlex

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
    metadata_path: str
    header_path: str
    etag_path: str
    licence_gate: str
    should_execute: bool
    supports_resume: bool
    captures_headers: bool
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


def _metadata_path(target: Path) -> Path:
    """Return the sidecar metadata path for a local raw target."""
    return target.with_suffix(f"{target.suffix}.metadata.json")


def _header_path(target: Path) -> Path:
    """Return the sidecar HTTP header path for a local raw target."""
    return target.with_suffix(f"{target.suffix}.headers")


def _etag_path(target: Path) -> Path:
    """Return the sidecar ETag cache path for a local raw target."""
    return target.with_suffix(f"{target.suffix}.etag")


def _shell_join(args: list[str]) -> str:
    """Render a shell-safe command preview from argv."""
    return " ".join(shlex.quote(arg) for arg in args)


def _curl_args(
    record: SourceFileRecord,
    target: Path,
    *,
    timeout_seconds: int = 180,
    resume_downloads: bool = False,
) -> list[str]:
    """Build a hardened curl argv for metadata-capturing downloads."""
    args = [
        "curl",
        "-L",
        "--fail",
        "--retry",
        "5",
        "--retry-all-errors",
        "--connect-timeout",
        "20",
        "--max-time",
        str(timeout_seconds),
        "--create-dirs",
        "--dump-header",
        str(_header_path(target)),
        "--etag-save",
        str(_etag_path(target)),
        "--etag-compare",
        str(_etag_path(target)),
    ]
    if resume_downloads:
        args.extend(["--continue-at", "-"])
    if record.acquisition_mode == "api_rate_limited":
        args.extend(["--header", "Accept: application/json, text/csv;q=0.9, */*;q=0.1"])
    args.extend(["-o", str(target), str(record.source_url)])
    return args


def _wget_args(
    record: SourceFileRecord,
    target: Path,
    *,
    timeout_seconds: int = 180,
    resume_downloads: bool = False,
) -> list[str]:
    """Build a hardened wget argv for metadata-capturing downloads."""
    args = [
        "wget",
        "--tries=5",
        "--timeout=20",
        f"--read-timeout={timeout_seconds}",
        "--server-response",
    ]
    if resume_downloads:
        args.append("--continue")
    if record.acquisition_mode == "api_rate_limited":
        args.extend(["--header=Accept: application/json, text/csv;q=0.9, */*;q=0.1"])
    args.extend(["-O", str(target), str(record.source_url)])
    return args


def build_download_plan(
    record: SourceFileRecord,
    *,
    output_dir: Path = Path("data/raw_live"),
    preferred_method: str = "curl",
    resume_downloads: bool = False,
) -> SourceDownloadPlan:
    """Build a shell acquisition plan without executing it."""
    target = safe_local_target(record, output_dir)
    executable = record.acquisition_mode in {"manual_download", "api_rate_limited"}
    if record.licence_gate in {"restricted_or_licence_review", "metadata_only"}:
        executable = False
    if record.file_role in {"landing_page", "licence_gate"}:
        executable = False
    args = (
        _wget_args(record, target, resume_downloads=resume_downloads)
        if preferred_method == "wget"
        else _curl_args(record, target, resume_downloads=resume_downloads)
    )
    command = f"mkdir -p {shlex.quote(str(target.parent))} && {_shell_join(args)}"
    return SourceDownloadPlan(
        source_file_id=record.id,
        method=preferred_method,
        command=command,
        target_path=str(target),
        metadata_path=str(_metadata_path(target)),
        header_path=str(_header_path(target)),
        etag_path=str(_etag_path(target)),
        licence_gate=record.licence_gate,
        should_execute=executable,
        supports_resume=resume_downloads,
        captures_headers=preferred_method == "curl",
        notes=(
            "Executable local raw download candidate with retries and header/ETag sidecars."
            if executable and not resume_downloads
            else (
                "Executable local raw download candidate with retries, resume support "
                "and header/ETag sidecars."
                if executable
                else "Metadata-only, landing-page or licence-gated record; do not auto-download."
            )
        ),
    )


def _sha_slug(value: str, *, length: int = 10) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def _file_sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _classify_failure(stderr: str) -> DownloadStatus:
    lowered = stderr.lower()
    if any(marker in lowered for marker in NETWORK_ERROR_MARKERS):
        return "blocked_network"
    return "failed"


def _resume_failure(stderr: str) -> bool:
    lowered = stderr.lower()
    return any(
        marker in lowered
        for marker in (
            "range",
            "resume",
            "content-range",
            "byte range",
            "does not support byte ranges",
        )
    )


def _compact_summary(text: str) -> str:
    """Collapse noisy multi-line command output into a single CSV-safe line."""
    return " ".join(text.split())


def _download_args(
    record: SourceFileRecord,
    target: Path,
    *,
    preferred_method: str,
    timeout_seconds: int,
    resume_downloads: bool,
) -> list[str]:
    if preferred_method == "wget":
        return _wget_args(
            record,
            target,
            timeout_seconds=timeout_seconds,
            resume_downloads=resume_downloads,
        )
    return _curl_args(
        record,
        target,
        timeout_seconds=timeout_seconds,
        resume_downloads=resume_downloads,
    )


def _write_attempt_metadata(
    *,
    record: SourceFileRecord,
    plan: SourceDownloadPlan,
    status: DownloadStatus,
    exit_code: int | None,
    bytes_downloaded: int,
    error_summary: str,
    attempted_at: str,
) -> None:
    """Write a local-only sidecar metadata record next to a raw download target."""
    metadata_path = Path(plan.metadata_path)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source_file_id": record.id,
        "source_id": record.source_id,
        "source_version_id": record.source_version_id,
        "attempted_at": attempted_at,
        "source_url": str(record.source_url),
        "target_path": plan.target_path,
        "header_path": plan.header_path,
        "etag_path": plan.etag_path,
        "status": status,
        "exit_code": exit_code,
        "bytes_downloaded": bytes_downloaded,
        "sha256": _file_sha256(Path(plan.target_path)),
        "licence_gate": record.licence_gate,
        "error_summary": error_summary[:500],
    }
    import json

    metadata_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def attempt_download(
    record: SourceFileRecord,
    *,
    output_dir: Path = Path("data/raw_live"),
    preferred_method: str = "curl",
    timeout_seconds: int = 60,
    resume_downloads: bool = False,
) -> DataAcquisitionAttemptRecord:
    """Attempt a local raw download with curl/wget, respecting licence gates."""
    plan = build_download_plan(
        record,
        output_dir=output_dir,
        preferred_method=preferred_method,
        resume_downloads=resume_downloads,
    )
    attempted_at = datetime.now(UTC).isoformat()
    target_path = Path(plan.target_path)
    attempt_id = f"attempt_{record.id}_{_sha_slug(attempted_at)}"
    if not plan.should_execute:
        attempt = DataAcquisitionAttemptRecord(
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
        _write_attempt_metadata(
            record=record,
            plan=plan,
            status="skipped_licence_gate",
            exit_code=None,
            bytes_downloaded=0,
            error_summary=plan.notes,
            attempted_at=attempted_at,
        )
        return attempt

    target_path.parent.mkdir(parents=True, exist_ok=True)
    args = _download_args(
        record,
        target_path,
        preferred_method=preferred_method,
        timeout_seconds=timeout_seconds,
        resume_downloads=resume_downloads,
    )
    # Fixed curl/wget argv; no shell expansion is used.
    completed = subprocess.run(  # nosec B603
        args,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds + 15,
    )
    if (
        completed.returncode != 0
        and resume_downloads
        and _resume_failure(completed.stderr + completed.stdout)
    ):
        args = _download_args(
            record,
            target_path,
            preferred_method=preferred_method,
            timeout_seconds=timeout_seconds,
            resume_downloads=False,
        )
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
        error_summary = _compact_summary(
            completed.stderr or completed.stdout or "Download command failed."
        )
        if target_path.exists() and bytes_downloaded == 0:
            target_path.unlink()
    error_summary = _compact_summary(error_summary)
    _write_attempt_metadata(
        record=record,
        plan=plan,
        status=status,
        exit_code=completed.returncode,
        bytes_downloaded=bytes_downloaded,
        error_summary=error_summary,
        attempted_at=attempted_at,
    )
    return DataAcquisitionAttemptRecord(
        id=attempt_id,
        source_file_id=record.id,
        attempted_at=attempted_at,
        method="curl" if preferred_method != "wget" else "wget",
        target_path=plan.target_path,
        status=status,
        exit_code=completed.returncode,
        bytes_downloaded=bytes_downloaded,
        command=_shell_join(args),
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
    # Route the generated launcher through the same Python acquisition path as
    # the CLI so shell downloads also emit attempt records and sidecars.
    method = plans[0].method if plans else "curl"
    resume_flag = " --resume-downloads" if any(plan.supports_resume for plan in plans) else ""
    command_lines = [
        'script_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)',
        'repo_root=$(CDPATH= cd -- "$script_dir/../../.." && pwd)',
        'cd "$repo_root"',
        (
            "PYTHONPATH=src uv run --all-extras python scripts/make_source_download_plan.py"
            f" --attempt --method {shlex.quote(method)}{resume_flag}"
        ),
    ]
    shell_path.write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\n\n" + "\n".join(command_lines) + "\n",
        encoding="utf-8",
    )
    shell_path.chmod(0o755)
    return plan_jsonl, plan_csv, attempt_jsonl, attempt_csv

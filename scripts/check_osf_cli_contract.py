"""Check the pinned OSF CLI surface without authenticating or mutating OSF."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess  # nosec B404 - the contract probe must execute the selected CLI binary
from pathlib import Path

EXPECTED_VERSION = "1.0.0"
REQUIRED_HELP_MARKERS = {
    "export": ("Export a node snapshot",),
    "files": ("upload", "versions"),
    "registrations": ("Create and inspect OSF registrations",),
    "validate": ("deterministic research profile",),
}


def _run(binary: str, *args: str) -> str:
    result = subprocess.run(  # nosec B603 - argv is a fixed list and shell execution is disabled
        [binary, *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if result.returncode != 0:
        command = " ".join((binary, *args))
        message = f"{command} failed with exit {result.returncode}: {result.stderr.strip()}"
        raise RuntimeError(message)
    return result.stdout


def validate_contract(binary: str, expected_version: str = EXPECTED_VERSION) -> list[str]:
    """Return contract failures for an unauthenticated OSF CLI binary."""
    failures: list[str] = []
    try:
        version = _run(binary, "--version").strip()
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        return [f"unable to execute OSF CLI: {exc}"]
    if version != expected_version:
        failures.append(f"expected OSF CLI {expected_version}, found {version}")

    for command, markers in REQUIRED_HELP_MARKERS.items():
        try:
            help_text = _run(binary, command, "--help")
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
            failures.append(f"{command} help unavailable: {exc}")
            continue
        for marker in markers:
            if marker not in help_text:
                failures.append(f"{command} help is missing marker: {marker}")

    try:
        upload_help = _run(binary, "files", "upload", "--help")
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        failures.append(f"files upload help unavailable: {exc}")
    else:
        for marker in ("--node", "--conflict"):
            if marker not in upload_help:
                failures.append(f"files upload help is missing marker: {marker}")
    return failures


def main() -> None:
    """Validate the pinned CLI and fail without reading credentials."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--binary",
        default=os.environ.get("OSF_BIN") or shutil.which("osf") or "osf",
        help="OSF CLI executable (default: OSF_BIN or PATH lookup)",
    )
    parser.add_argument("--expected-version", default=EXPECTED_VERSION)
    args = parser.parse_args()
    failures = validate_contract(args.binary, args.expected_version)
    if failures:
        raise SystemExit("OSF CLI contract failed: " + "; ".join(failures))
    print(f"OSF CLI contract passed: {Path(args.binary).name} {args.expected_version}")


if __name__ == "__main__":
    main()

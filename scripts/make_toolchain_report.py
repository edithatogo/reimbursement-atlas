"""Generate a local toolchain availability report with lightweight CLI probes."""

from __future__ import annotations

import csv
import json
import platform
import shutil
import subprocess  # nosec B404
import sys
from dataclasses import asdict, dataclass
from importlib import metadata
from itertools import starmap
from pathlib import Path
from typing import cast

from reimburse_atlas.toolchain import classify_gate_result

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_PATH = REPO_ROOT / "data" / "derived" / "toolchain_report.json"
DEFAULT_CSV_PATH = REPO_ROOT / "data" / "derived" / "toolchain_report.csv"

PYTHON_PACKAGES: tuple[tuple[str, str, str], ...] = (
    ("ruff", "python-package", "ruff"),
    ("basedpyright", "python-package", "basedpyright"),
    ("pytest", "python-package", "pytest"),
    ("pytest-cov", "python-package", "pytest-cov"),
    ("hypothesis", "python-package", "hypothesis"),
    ("mutmut", "python-package", "mutmut"),
    ("scalene", "python-package", "scalene"),
    ("bandit", "python-package", "bandit"),
    ("pip-audit", "python-package", "pip-audit"),
    ("polars", "python-package", "polars"),
    ("pyarrow", "python-package", "pyarrow"),
    ("duckdb", "python-package", "duckdb"),
    ("lancedb", "python-package", "lancedb"),
    ("pydantic", "python-package", "pydantic"),
    ("defusedxml", "python-package", "defusedxml"),
    ("fastapi", "python-package", "fastapi"),
    ("mcp", "python-package", "mcp"),
)

CLI_PROBES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("uv", ("uv", "--version")),
    ("official-pixi-on-path", ("pixi", "--version")),
    ("mojo-on-path", ("mojo", "--version")),
    ("mojo-via-uv-tool", ("uv", "tool", "run", "--from", "mojo-compiler", "mojo", "--version")),
    ("node", ("node", "--version")),
    ("npm", ("npm", "--version")),
)

NODE_PACKAGES: tuple[str, ...] = (
    "astro",
    "@astrojs/check",
    "@astrojs/react",
    "@cosmograph/react",
    "papaparse",
    "typescript",
    "react",
    "react-dom",
)

DASHBOARD_LOCKFILE = REPO_ROOT / "apps" / "dashboard" / "package-lock.json"
UV_LOCKFILE = REPO_ROOT / "uv.lock"


@dataclass(frozen=True)
class ToolchainRow:
    """One detected local toolchain capability."""

    name: str
    kind: str
    available: bool
    version: str
    path: str
    notes: str


def _public_cli_path(executable: str) -> str:
    """Return a stable executable reference without exposing a machine path."""
    return f"PATH:{executable}"


def package_row(name: str, kind: str, distribution: str) -> ToolchainRow:
    """Return one package availability row from installed distribution metadata."""
    try:
        version = metadata.version(distribution)
    except metadata.PackageNotFoundError:
        return ToolchainRow(
            name=name,
            kind=kind,
            available=False,
            version="",
            path="",
            notes="not installed in active Python environment",
        )
    return ToolchainRow(
        name=name,
        kind=kind,
        available=True,
        version=version,
        path="python environment",
        notes="installed",
    )


def node_package_row(name: str) -> ToolchainRow:
    """Return one dashboard package row from package-lock metadata."""
    if not DASHBOARD_LOCKFILE.exists():
        return ToolchainRow(
            name=name,
            kind="node-package",
            available=False,
            version="",
            path="",
            notes="apps/dashboard/package-lock.json missing",
        )
    payload: object = json.loads(DASHBOARD_LOCKFILE.read_text(encoding="utf-8"))
    packages_raw: object = {}
    if isinstance(payload, dict):
        payload_dict = cast("dict[str, object]", payload)
        packages_raw = payload_dict.get("packages", {})
    packages = cast("dict[str, object]", packages_raw) if isinstance(packages_raw, dict) else {}
    entry_raw = packages.get(f"node_modules/{name}")
    if not isinstance(entry_raw, dict):
        return ToolchainRow(
            name=name,
            kind="node-package",
            available=False,
            version="",
            path="apps/dashboard/package-lock.json",
            notes="not found in dashboard lockfile",
        )
    entry = cast("dict[str, object]", entry_raw)
    version = entry.get("version")
    return ToolchainRow(
        name=name,
        kind="node-package",
        available=True,
        version=version if isinstance(version, str) else "",
        path="apps/dashboard/package-lock.json",
        notes="locked",
    )


def lockfile_row(path: Path, name: str) -> ToolchainRow:
    """Return one row indicating whether a reproducibility lockfile exists."""
    return ToolchainRow(
        name=name,
        kind="lockfile",
        available=path.exists(),
        version="",
        path=str(path.relative_to(REPO_ROOT)) if path.exists() else "",
        notes="present" if path.exists() else "missing",
    )


def cli_probe_row(name: str, command: tuple[str, ...]) -> ToolchainRow:
    """Return one executable availability row using PATH lookup and a short probe."""
    executable = command[0]
    path = shutil.which(executable)
    if path is None:
        return ToolchainRow(
            name=name,
            kind="cli",
            available=False,
            version="",
            path="",
            notes="not found on PATH",
        )
    try:
        completed = subprocess.run(  # nosec B603
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return ToolchainRow(
            name=name,
            kind="cli",
            available=False,
            version="",
            path=_public_cli_path(executable),
            notes="probe timed out",
        )
    except OSError as exc:
        return ToolchainRow(
            name=name,
            kind="cli",
            available=False,
            version="",
            path=_public_cli_path(executable),
            notes=f"probe failed: {exc}",
        )
    outcome = classify_gate_result(completed.returncode, completed.stdout, completed.stderr)
    version = (
        (completed.stdout or completed.stderr).strip().splitlines()[0]
        if (completed.stdout or completed.stderr).strip()
        else ""
    )
    if outcome == "passed":
        notes = "probe passed"
        available = True
    elif outcome == "wrong_tool":
        notes = "same-named executable is not the expected official tool"
        available = False
    elif outcome == "blocked_network":
        notes = "probe reached an external-network blocker"
        available = False
    else:
        notes = f"probe outcome: {outcome}"
        available = False
    return ToolchainRow(
        name=name,
        kind="cli",
        available=available,
        version=version,
        path=_public_cli_path(executable),
        notes=notes,
    )


def build_rows() -> list[ToolchainRow]:
    """Build the local toolchain report rows."""
    rows = [
        ToolchainRow(
            name="python",
            kind="runtime",
            available=True,
            version=platform.python_version(),
            path="active Python interpreter",
            notes=f"{platform.system()} {platform.machine()} via {Path(sys.executable).name}",
        ),
    ]
    rows.extend(starmap(package_row, PYTHON_PACKAGES))
    rows.extend(node_package_row(name) for name in NODE_PACKAGES)
    rows.extend((
        lockfile_row(UV_LOCKFILE, "uv.lock"),
        lockfile_row(DASHBOARD_LOCKFILE, "dashboard package-lock"),
    ))
    rows.extend(starmap(cli_probe_row, CLI_PROBES))
    return rows


def write_report(json_path: Path = DEFAULT_JSON_PATH, csv_path: Path = DEFAULT_CSV_PATH) -> None:
    """Write JSON and CSV toolchain report files."""
    rows = build_rows()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "generated_by": "scripts/make_toolchain_report.py",
        "rows": [asdict(row) for row in rows],
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["name", "kind", "available", "version", "path", "notes"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def main() -> None:
    """CLI entrypoint."""
    write_report()


if __name__ == "__main__":
    main()

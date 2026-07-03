"""Generate a local toolchain availability report without shelling out to tools."""

from __future__ import annotations

import csv
import json
import platform
import shutil
import sys
from dataclasses import asdict, dataclass
from importlib import metadata
from itertools import starmap
from pathlib import Path

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

CLI_TOOLS: tuple[str, ...] = ("uv", "pixi", "mojo", "node", "npm")


@dataclass(frozen=True)
class ToolchainRow:
    """One detected local toolchain capability."""

    name: str
    kind: str
    available: bool
    version: str
    path: str
    notes: str


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


def cli_row(name: str) -> ToolchainRow:
    """Return one executable availability row using PATH lookup only."""
    path = shutil.which(name)
    return ToolchainRow(
        name=name,
        kind="cli",
        available=path is not None,
        version="",
        path="PATH" if path is not None else "",
        notes="found on PATH" if path is not None else "not found on PATH",
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
    rows.extend(cli_row(name) for name in CLI_TOOLS)
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
        )
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def main() -> None:
    """CLI entrypoint."""
    write_report()


if __name__ == "__main__":
    main()

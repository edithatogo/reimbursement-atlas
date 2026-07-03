"""Optional local analytical warehouse helpers.

The module imports DuckDB and Polars lazily so the lightweight registry tests can
run without native analytical dependencies installed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from reimburse_atlas.registry import project_root


class OptionalDependencyError(RuntimeError):
    """Raised when an optional analytical dependency is missing."""


def _import_optional(name: str) -> Any:
    try:
        return __import__(name)
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on local env
        msg = f"Optional dependency '{name}' is required for this warehouse operation."
        raise OptionalDependencyError(msg) from exc


def build_seed_duckdb(database_path: Path | str = ":memory:", seed_dir: Path | None = None) -> Any:
    """Create a DuckDB database containing the seed registries."""
    duckdb = _import_optional("duckdb")
    polars = _import_optional("polars")

    base = seed_dir or project_root() / "data" / "seed"
    con = duckdb.connect(str(database_path))
    for name in ("source_registry", "analysis_catalogue", "ontology_registry"):
        frame = polars.read_csv(base / f"{name}.csv")
        con.register(name, frame.to_arrow())
        con.execute(f"create or replace table {name} as select * from {name}")  # nosec B608
    return con

"""Protect the Pixi-to-uv boundary for Python security and build gates."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_python_security_and_build_tasks_use_locked_uv_runner() -> None:
    """Pixi task names must remain executable in a fresh default environment."""
    with (ROOT / "pyproject.toml").open("rb") as handle:
        tasks = tomllib.load(handle)["tool"]["pixi"]["tasks"]

    assert tasks["bandit"].startswith("uv run --all-extras bandit ")
    assert tasks["pip-audit"] == "uv run --all-extras pip-audit --strict"
    assert tasks["build"] == "uv build"

"""Protect the Pixi-to-uv boundary for Python security and build gates."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_python_security_and_build_tasks_use_locked_uv_runner() -> None:
    """Pixi task names must remain executable in a fresh default environment."""
    with (ROOT / "pyproject.toml").open("rb") as handle:
        tasks = tomllib.load(handle)["tool"]["pixi"]["tasks"]

    assert tasks["bandit"].startswith("uv run --all-extras bandit ")
    assert tasks["pip-audit"] == "bash scripts/run_pip_audit.sh"
    assert tasks["build"] == "uv build"


def test_active_mapping_tasks_target_registry_active_cycle() -> None:
    """Canonical regeneration must not silently operate on a superseded study."""
    with (ROOT / "pyproject.toml").open("rb") as handle:
        tasks = tomllib.load(handle)["tool"]["pixi"]["tasks"]
    registry = json.loads(
        (ROOT / "data/derived/mapping_study/cycle_registry.json").read_text(encoding="utf-8")
    )
    expected = f"--cycle {registry['active_cycle']}"

    active_tasks = (
        "mapping-active-review-packets",
        "mapping-active-review-ledger",
        "mapping-active-adjudication",
        "mapping-active-split",
        "mapping-active-threshold",
        "mapping-active-evaluation",
    )
    assert all(expected in tasks[name] for name in active_tasks)


def test_dashboard_owner_packet_task_imports_repository_scripts() -> None:
    """The declared task must expose both source and repository modules."""
    with (ROOT / "pyproject.toml").open("rb") as handle:
        tasks = tomllib.load(handle)["tool"]["pixi"]["tasks"]

    assert tasks["dashboard-owner-review-packet"].startswith("PYTHONPATH=.:src ")
    assert tasks["dashboard-owner-review-packet-refresh"].endswith(
        "make_dashboard_owner_review_packet.py --refresh"
    )

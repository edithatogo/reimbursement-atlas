"""Tests for the portable mutation timeout wrapper."""

from __future__ import annotations

import sys
import time

from scripts.run_bounded_mutation import MUTMUT_COMMAND, run_bounded


def test_mutmut_command_uses_current_configuration_contract() -> None:
    """Mutmut 3 reads source and worker settings from ``pyproject.toml``."""
    assert MUTMUT_COMMAND == ("mutmut", "run", "--max-children", "2")


def test_run_bounded_returns_child_status() -> None:
    """Successful mutation commands preserve their exit status."""
    assert run_bounded((sys.executable, "-c", "raise SystemExit(7)"), 2) == 7


def test_run_bounded_terminates_timed_out_process() -> None:
    """A hung child is terminated and reported with the conventional timeout code."""
    started = time.monotonic()
    result = run_bounded((sys.executable, "-c", "import time; time.sleep(10)"), 1)
    assert result == 124
    assert time.monotonic() - started < 5

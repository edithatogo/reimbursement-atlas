"""Tests for licence gate evaluation."""

from __future__ import annotations

from reimburse_atlas.licensing import evaluate_licence_gates
from reimburse_atlas.registry import load_source_registry


def test_licence_gates_return_all_sources() -> None:
    """Every source should have an explicit publication gate."""
    sources = load_source_registry()
    gates = evaluate_licence_gates(sources)
    assert len(gates) == len(sources)
    assert {gate.status for gate in gates} <= {"green", "amber", "red"}

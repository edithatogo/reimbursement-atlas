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


def test_cms_data_terms_are_not_relicensed_as_apache() -> None:
    """CMS/AMA terms remain distinct from the repository code licence."""
    source = next(source for source in load_source_registry() if source.id == "us_cms_clfs")

    assert "CMS/AMA" in source.licence_notes
    assert "Apache-2.0" in source.licence_notes
    assert "CPT descriptors" in source.licence_notes

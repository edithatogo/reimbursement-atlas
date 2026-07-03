"""Smoke tests for repository design assets."""

from __future__ import annotations

from pathlib import Path


def test_required_design_files_exist(repo_root: Path) -> None:
    """Core planning files should exist."""
    required = [
        "README.md",
        "REQUIREMENTS.md",
        "DESIGN.md",
        "docs/SOURCES.md",
        "docs/ANALYSES.md",
        "conductor/INDEX.md",
        "data/seed/source_registry.jsonl",
        "apps/dashboard/package.json",
    ]
    for relative in required:
        assert (repo_root / relative).exists(), relative


def test_design_contains_mermaid(repo_root: Path) -> None:
    """Design file should contain Mermaid diagrams."""
    design = (repo_root / "DESIGN.md").read_text(encoding="utf-8")
    assert "```mermaid" in design
    assert "flowchart" in design

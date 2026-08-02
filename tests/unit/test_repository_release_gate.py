"""Tests for the repository-only software release gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.validate_repository_release_gate import main


def test_repository_release_gate_ignores_research_readiness(
    repo_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A software release can proceed while research publication remains blocked."""
    summary_path = repo_root / "data/derived/release_readiness/summary.json"
    original = summary_path.read_text(encoding="utf-8")
    try:
        summary = json.loads(original)
        summary.update(
            repository_release_ready=True,
            evidence_release_ready=False,
            research_publication_ready=False,
        )
        summary_path.write_text(json.dumps(summary), encoding="utf-8")
        monkeypatch.chdir(repo_root)
        main()
        assert json.loads(capsys.readouterr().out)["status"] == "ready"
    finally:
        summary_path.write_text(original, encoding="utf-8")

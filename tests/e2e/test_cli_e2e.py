"""End-to-end CLI tests."""

from __future__ import annotations

from typer.testing import CliRunner

from reimburse_atlas.cli import app


def test_cli_validate_e2e() -> None:
    """The validate command should succeed with seed data."""
    result = CliRunner().invoke(app, ["validate"])
    assert result.exit_code == 0
    assert "source_count" in result.output


def test_cli_export_graph_e2e(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """The export-graph command should write node and edge files."""
    result = CliRunner().invoke(app, ["export-graph", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "graph_nodes.csv").exists()
    assert (tmp_path / "graph_edges.csv").exists()


def test_cli_validate_seed_files_e2e() -> None:
    """The validate-seed-files command should succeed with generated CSV mirrors."""
    result = CliRunner().invoke(app, ["validate-seed-files"])
    assert result.exit_code == 0
    assert "Seed JSONL/CSV sync" in result.output


def test_cli_publication_manifest_e2e(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """The publication-manifest command should write a manifest."""
    target = tmp_path / "publication_manifest.json"
    result = CliRunner().invoke(app, ["publication-manifest", str(target)])
    assert result.exit_code == 0
    assert target.exists()

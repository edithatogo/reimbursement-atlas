"""Contracts for dependency automation and scheduled tool availability."""

from __future__ import annotations

import tomllib

import yaml

from reimburse_atlas.registry import project_root


def test_dependabot_defers_typescript7_to_compatibility_canary() -> None:
    """Dependabot must not bypass the explicit TypeScript compatibility gate."""
    config = yaml.safe_load((project_root() / ".github/dependabot.yml").read_text())
    npm = next(update for update in config["updates"] if update["package-ecosystem"] == "npm")
    ignored = {item["dependency-name"]: item["versions"] for item in npm["ignore"]}
    assert ignored["typescript"] == [">=7"]


def test_default_pixi_environment_installs_mutation_runner() -> None:
    """The scheduled Pixi mutation task must include its executable."""
    pyproject = (project_root() / "pyproject.toml").read_text(encoding="utf-8")
    section = pyproject.split("[tool.pixi.feature.mutation.pypi-dependencies]", 1)[1].split(
        "\n[", 1
    )[0]
    assert 'mutmut = ">=3.7.0"' in section
    assert 'mutation = { features = ["mutation"], solve-group = "default" }' in pyproject
    workflow = (project_root() / ".github/workflows/mutation-nightly.yml").read_text(
        encoding="utf-8"
    )
    assert "pixi run --environment mutation mutation" in workflow


def test_mutation_workspace_copies_test_runtime_dependencies() -> None:
    """Mutmut's isolated workspace must contain modules imported by unit tests."""
    config = tomllib.loads((project_root() / "pyproject.toml").read_text(encoding="utf-8"))
    mutation = config["tool"]["mutmut"]
    assert mutation["source_paths"] == ["src/reimburse_atlas"]
    copied = set(mutation["also_copy"])
    assert {".github", "apps", "conductor", "data", "docs", "schema", "scripts"} <= copied
    assert {".zenodo.json", "ARTIFACT_MANIFEST.json", "CITATION.cff"} <= copied
    assert "mutate_only_covered_lines" not in mutation

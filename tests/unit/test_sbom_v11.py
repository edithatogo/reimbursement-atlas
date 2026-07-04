from __future__ import annotations

from pathlib import Path

from reimburse_atlas.sbom import (
    build_dashboard_sbom,
    build_python_sbom,
    dependency_name,
    sbom_summary,
)


def test_dependency_name_parses_pep508() -> None:
    assert dependency_name("polars>=1.35.0") == "polars"
    assert dependency_name("pydantic-settings>=2; python_version >= '3.13'") == "pydantic-settings"


def test_build_python_sbom_from_repo_lock() -> None:
    root = Path(__file__).resolve().parents[2]
    sbom = build_python_sbom(root)
    summary = sbom_summary(sbom)
    assert sbom["bomFormat"] == "CycloneDX"
    assert sbom["specVersion"] == "1.6"
    assert int(summary["component_count"]) > 10
    assert summary["ecosystem"] == "python"


def test_build_dashboard_sbom_from_package_lock() -> None:
    root = Path(__file__).resolve().parents[2]
    sbom = build_dashboard_sbom(root)
    summary = sbom_summary(sbom)
    assert sbom["bomFormat"] == "CycloneDX"
    assert int(summary["component_count"]) > 5
    assert summary["ecosystem"] == "npm"

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.architecture import (
    build_architecture_report,
    build_layer_policy_records,
    find_import_cycles,
    layer_for_module,
    scan_import_edges,
    write_architecture_report,
)


def test_layer_for_module_known_and_unknown() -> None:
    assert layer_for_module("reimburse_atlas.models") == "foundation"
    assert layer_for_module("reimburse_atlas.cli") == "interface"
    assert layer_for_module("reimburse_atlas.not_a_real_module") == "unknown"


def test_architecture_report_for_repo_is_ready() -> None:
    report = build_architecture_report(Path(__file__).resolve().parents[2])
    assert report.summary.edge_count > 0
    assert report.summary.layer_violation_count == 0
    assert report.summary.unknown_layer_count == 0
    assert report.summary.architecture_ready is True


def test_architecture_detects_layer_violation(tmp_path: Path) -> None:
    package = tmp_path / "src" / "reimburse_atlas"
    package.mkdir(parents=True)
    (package / "models.py").write_text(
        "from reimburse_atlas.cli import app\n",
        encoding="utf-8",
    )
    (package / "cli.py").write_text("app = object()\n", encoding="utf-8")
    edges = scan_import_edges(tmp_path)
    assert any(not edge.allowed for edge in edges)
    policies = build_layer_policy_records(edges)
    assert any(policy.status == "fail" for policy in policies)


def test_architecture_cycle_detection_and_write(tmp_path: Path) -> None:
    package = tmp_path / "src" / "reimburse_atlas"
    package.mkdir(parents=True)
    (package / "models.py").write_text(
        "from reimburse_atlas.contracts import Thing\n",
        encoding="utf-8",
    )
    (package / "contracts.py").write_text(
        "from reimburse_atlas.models import Other\n",
        encoding="utf-8",
    )
    report = build_architecture_report(tmp_path)
    cycles = find_import_cycles(list(report.edges))
    assert cycles
    paths = write_architecture_report(report, output_dir=tmp_path / "out")
    assert all(path.exists() for path in paths)

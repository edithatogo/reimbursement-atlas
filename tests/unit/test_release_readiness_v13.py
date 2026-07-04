from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.io import write_csv
from reimburse_atlas.release_readiness import (
    ReleaseGateRecord,
    build_release_readiness_report,
    summarise_release_gates,
    write_release_readiness_report,
)


def test_release_summary_tracks_required_blockers() -> None:
    gates = [
        ReleaseGateRecord(
            id="required_pass",
            category="security",
            status="pass",
            required=True,
            evidence="ok",
            recommended_action="none",
        ),
        ReleaseGateRecord(
            id="required_blocked",
            category="security",
            status="blocked",
            required=True,
            evidence="dns",
            recommended_action="rerun in CI",
        ),
        ReleaseGateRecord(
            id="optional_fail",
            category="supply_chain",
            status="fail",
            required=False,
            evidence="advisory",
            recommended_action="pin actions",
        ),
    ]
    summary = summarise_release_gates(gates)
    assert summary.gate_count == 3
    assert summary.required_blocker_count == 1
    assert summary.public_release_ready is False


def test_release_readiness_report_reads_generated_evidence(tmp_path: Path) -> None:
    (tmp_path / "data/derived/local_quality_gates").mkdir(parents=True)
    external_gate_path = tmp_path / "data/derived/external_quality_gates.json"
    external_gate_path.parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "data/derived/repo_automation").mkdir(parents=True)
    (tmp_path / "data/derived/sbom").mkdir(parents=True)
    (tmp_path / "data/derived/architecture").mkdir(parents=True)

    (tmp_path / "data/derived/local_quality_gates/summary.json").write_text(
        json.dumps({"profile": "ci", "release_ready": True, "blocking_failures": 0}),
        encoding="utf-8",
    )
    write_csv(
        [
            {"id": gate, "status": "passed", "return_code": 0}
            for gate in (
                "ruff_check",
                "ruff_format_check",
                "basedpyright",
                "pytest_coverage",
                "bandit",
                "public_data_policy",
                "seed_sync",
                "uv_build",
                "dashboard_build",
            )
        ],
        tmp_path / "data/derived/local_quality_gates/local_quality_gates.csv",
    )
    external_gate_path.write_text(
        json.dumps({
            "records": [
                {"id": "pip_audit_strict", "outcome": "passed", "return_code": 0},
                {"id": "npm_audit_dashboard", "outcome": "passed", "return_code": 0},
                {"id": "zizmor_workflow_security", "outcome": "passed", "return_code": 0},
                {"id": "pixi_available", "outcome": "passed", "return_code": 0},
                {"id": "mojo_available_uv_tool", "outcome": "passed", "return_code": 0},
            ]
        }),
        encoding="utf-8",
    )
    (tmp_path / "data/derived/repo_automation/summary.json").write_text(
        json.dumps({"fail": 0, "warn": 0, "pass": 10}),
        encoding="utf-8",
    )
    write_csv([], tmp_path / "data/derived/repo_automation/action_sha_pin_plan.csv")
    write_csv(
        [
            {"component_count": 2, "name": "python"},
            {"component_count": 3, "name": "dashboard"},
        ],
        tmp_path / "data/derived/sbom/sbom_summary.csv",
    )
    (tmp_path / "data/derived/architecture/summary.json").write_text(
        json.dumps({
            "layer_violation_count": 0,
            "internal_cycle_count": 0,
            "unknown_layer_count": 0,
        }),
        encoding="utf-8",
    )
    (tmp_path / "data/derived/publication_manifest.json").write_text(
        json.dumps({"artifact_count": 4, "warnings": []}),
        encoding="utf-8",
    )

    report = build_release_readiness_report(tmp_path)
    assert report.summary.required_blocker_count == 0
    assert report.summary.public_release_ready is True
    paths = write_release_readiness_report(report, output_dir=tmp_path / "release")
    assert all(path.exists() for path in paths)

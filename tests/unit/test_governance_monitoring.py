"""Tests for canonical external governance-monitor evidence."""

from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.governance_monitoring import build_governance_monitor_report
from reimburse_atlas.release_readiness import governance_monitor_gates, summarise_release_gates


def _typescript(status: str = "blocked_peer") -> dict[str, object]:
    return {
        "status": status,
        "checker": "@astrojs/check",
        "checker_version": "0.9.9",
        "checker_peer_typescript": "^5 || ^6",
        "candidate_typescript7": "7.0.2",
        "mutation_performed": False,
    }


def _github(*, advanced: str = "disabled") -> dict[str, object]:
    return {
        "status": "blocked_account" if advanced != "enabled" else "pass",
        "controls": {
            "secret_scanning": "enabled",
            "secret_scanning_push_protection": "enabled",
            "secret_scanning_non_provider_patterns": advanced,
            "secret_scanning_validity_checks": advanced,
        },
        "mutation_performed": False,
    }


def test_report_classifies_external_platform_boundaries() -> None:
    report = build_governance_monitor_report(
        typescript_report=_typescript(),
        github_report=_github(),
    )

    assert report.summary.external_blocker_count == 3
    assert report.summary.repository_release_blocker_count == 0
    assert {record.reason_code for record in report.records} == {
        "checker_peer_excludes_typescript7",
        "github_account_capability_unavailable",
    }
    assert all(not record.required_for_repository_release for record in report.records)
    assert all(not record.mutation_performed for record in report.records)


def test_report_exposes_reviewable_typescript_upgrade_without_mutation() -> None:
    report = build_governance_monitor_report(
        typescript_report=_typescript("upgrade_available"),
        github_report=_github(advanced="enabled"),
    )

    assert report.summary.external_blocker_count == 0
    assert report.records[0].status == "action_available"
    assert report.records[0].reason_code == "upstream_compatibility_available"


def test_missing_or_permission_limited_evidence_fails_closed() -> None:
    report = build_governance_monitor_report(
        typescript_report={},
        github_report={"status": "blocked_permissions", "controls": {}},
    )

    assert report.summary.external_blocker_count == 3
    assert {record.reason_code for record in report.records} == {
        "monitor_evidence_missing",
        "github_security_visibility_insufficient",
    }


def test_external_governance_gates_do_not_block_repository_release(tmp_path: Path) -> None:
    output = tmp_path / "data/derived/governance_monitoring"
    output.mkdir(parents=True)
    rows = [
        record.as_row()
        for record in build_governance_monitor_report(
            typescript_report=_typescript(),
            github_report=_github(),
        ).records
    ]
    (output / "external_controls.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    gates = governance_monitor_gates(tmp_path)
    summary = summarise_release_gates(gates)

    assert len(gates) == 3
    assert all(gate.status == "blocked" and not gate.required for gate in gates)
    assert summary.required_blocker_count == 0
    assert summary.repository_release_ready is True

"""Canonical evidence for externally controlled compatibility and security gates."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

from reimburse_atlas.io import write_csv, write_jsonl

ExternalControlStatus = Literal["pass", "blocked_external", "action_available"]
ExternalControlScope = Literal["external_dependency", "external_account_capability"]


@dataclass(frozen=True)
class ExternalControlRecord:
    """One externally controlled governance observation."""

    id: str
    scope: ExternalControlScope
    status: ExternalControlStatus
    reason_code: str
    evidence_path: str
    observed_value: str
    required_for_repository_release: bool
    mutation_performed: bool
    recommended_action: str

    def as_row(self) -> dict[str, object]:
        """Return a serialization-safe record."""
        return asdict(self)


@dataclass(frozen=True)
class GovernanceMonitorSummary:
    """Summary of current external governance controls."""

    schema_version: str
    control_count: int
    pass_count: int
    action_available_count: int
    external_blocker_count: int
    repository_release_blocker_count: int

    def as_row(self) -> dict[str, object]:
        """Return a serialization-safe summary."""
        return asdict(self)


@dataclass(frozen=True)
class GovernanceMonitorReport:
    """Canonical external-control report."""

    records: tuple[ExternalControlRecord, ...]
    summary: GovernanceMonitorSummary


def build_governance_monitor_report(
    *,
    typescript_report: dict[str, Any],
    github_report: dict[str, Any],
) -> GovernanceMonitorReport:
    """Normalize existing monitor outputs without granting mutation authority."""
    records = (_typescript_record(typescript_report), *_github_advanced_records(github_report))
    summary = GovernanceMonitorSummary(
        schema_version="external-governance-monitor-v1",
        control_count=len(records),
        pass_count=sum(record.status == "pass" for record in records),
        action_available_count=sum(record.status == "action_available" for record in records),
        external_blocker_count=sum(record.status == "blocked_external" for record in records),
        repository_release_blocker_count=sum(
            record.status == "blocked_external" and record.required_for_repository_release
            for record in records
        ),
    )
    return GovernanceMonitorReport(records=records, summary=summary)


def write_governance_monitor_report(
    report: GovernanceMonitorReport,
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write deterministic JSONL, CSV and summary evidence."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [record.as_row() for record in report.records]
    jsonl_path = write_jsonl(rows, output_dir / "external_controls.jsonl")
    csv_path = write_csv(rows, output_dir / "external_controls.csv")
    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(report.summary.as_row(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return jsonl_path, csv_path, summary_path


def _typescript_record(report: dict[str, Any]) -> ExternalControlRecord:
    status = str(report.get("status", ""))
    observed = (
        f"checker={report.get('checker', 'unknown')}@{report.get('checker_version', 'unknown')} "
        f"peer={report.get('checker_peer_typescript', 'unknown')} "
        f"candidate={report.get('candidate_typescript7', 'unknown')}"
    )
    if status == "upgrade_available":
        return _record(
            identifier="typescript7_astro_compatibility",
            scope="external_dependency",
            status="action_available",
            reason_code="upstream_compatibility_available",
            evidence_path="data/derived/toolchain/typescript_compatibility.json",
            observed_value=observed,
            recommended_action=(
                "Open a normal upgrade PR and run npm, Astro, build and browser gates."
            ),
        )
    reason_code = {
        "blocked_peer": "checker_peer_excludes_typescript7",
        "blocked_network": "npm_registry_unavailable",
        "unknown": "npm_registry_unavailable",
    }.get(status, "monitor_evidence_missing")
    return _record(
        identifier="typescript7_astro_compatibility",
        scope="external_dependency",
        status="blocked_external",
        reason_code=reason_code,
        evidence_path="data/derived/toolchain/typescript_compatibility.json",
        observed_value=observed,
        recommended_action="Continue the read-only canary until the checker peer range admits 7.x.",
    )


def _github_advanced_records(report: dict[str, Any]) -> tuple[ExternalControlRecord, ...]:
    controls_value = report.get("controls")
    controls = cast("dict[str, object]", controls_value) if isinstance(controls_value, dict) else {}
    report_status = str(report.get("status", ""))
    records: list[ExternalControlRecord] = []
    for key in (
        "secret_scanning_non_provider_patterns",
        "secret_scanning_validity_checks",
    ):
        observed = str(controls.get(key, "unknown"))
        if observed == "enabled":
            status: ExternalControlStatus = "pass"
            reason_code = "control_enabled"
            action = "No account-level action is required."
        else:
            status = "blocked_external"
            reason_code = (
                "github_security_visibility_insufficient"
                if report_status in {"blocked_permissions", "blocked_environment"}
                else "github_account_capability_unavailable"
            )
            action = "Enable the account/plan capability when GitHub makes it available."
        records.append(
            _record(
                identifier=f"github_account_{key}",
                scope="external_account_capability",
                status=status,
                reason_code=reason_code,
                evidence_path=("data/derived/repo_automation/github_security_settings.json"),
                observed_value=observed,
                recommended_action=action,
            )
        )
    return tuple(records)


def _record(
    *,
    identifier: str,
    scope: ExternalControlScope,
    status: ExternalControlStatus,
    reason_code: str,
    evidence_path: str,
    observed_value: str,
    recommended_action: str,
) -> ExternalControlRecord:
    return ExternalControlRecord(
        id=identifier,
        scope=scope,
        status=status,
        reason_code=reason_code,
        evidence_path=evidence_path,
        observed_value=observed_value,
        required_for_repository_release=False,
        mutation_performed=False,
        recommended_action=recommended_action,
    )

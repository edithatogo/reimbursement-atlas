"""Release-readiness gates for public, derived-data and software releases."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.registry import project_root

ReleaseGateStatus = Literal["pass", "warn", "fail", "blocked", "missing"]
ReleaseGateCategory = Literal[
    "code_quality",
    "security",
    "supply_chain",
    "data_governance",
    "architecture",
    "dashboard",
    "release",
    "toolchain",
]


@dataclass(frozen=True)
class ReleaseGateRecord:
    """One release-readiness gate."""

    id: str
    category: ReleaseGateCategory
    status: ReleaseGateStatus
    required: bool
    evidence: str
    recommended_action: str

    def as_row(self) -> dict[str, object]:
        """Return a CSV/JSON-safe row."""
        return asdict(self)


@dataclass(frozen=True)
class ReleaseReadinessSummary:
    """Summary of the release-readiness matrix."""

    schema_version: str
    gate_count: int
    pass_count: int
    warn_count: int
    fail_count: int
    blocked_count: int
    missing_count: int
    required_blocker_count: int
    repository_release_ready: bool
    research_publication_ready: bool
    osf_registration_ready: bool
    evidence_release_ready: bool
    policy_claims_ready: bool

    def as_row(self) -> dict[str, object]:
        """Return a CSV/JSON-safe row."""
        return asdict(self)


@dataclass(frozen=True)
class ReleaseReadinessReport:
    """Full release-readiness report."""

    gates: tuple[ReleaseGateRecord, ...]
    summary: ReleaseReadinessSummary


def build_release_readiness_report(root: Path | None = None) -> ReleaseReadinessReport:
    """Build a consolidated release-readiness report from generated artefacts."""
    repo = root or project_root()
    gates = [
        _local_quality_gate(repo),
        _local_gate_status(repo, "ruff_check", "code_quality", required=True),
        _local_gate_status(repo, "ruff_format_check", "code_quality", required=True),
        _local_gate_status(repo, "basedpyright", "code_quality", required=True),
        _local_gate_status(repo, "pytest_coverage", "code_quality", required=True),
        _local_gate_status(repo, "bandit", "security", required=True),
        _local_gate_status(repo, "public_data_policy", "data_governance", required=True),
        _local_gate_status(repo, "seed_sync", "data_governance", required=True),
        _local_gate_status(repo, "protocol_status", "data_governance", required=True),
        _local_gate_status(repo, "source_content_validation", "data_governance", required=True),
        _local_gate_status(repo, "roadmap_linkages", "data_governance", required=True),
        _local_gate_status(repo, "data_quality", "data_governance", required=True),
        _local_gate_status(repo, "data_dictionary", "data_governance", required=True),
        _local_gate_status(repo, "evidence_readiness", "data_governance", required=True),
        _local_gate_status(repo, "source_drift", "data_governance", required=True),
        _data_quality_gate(repo),
        _data_dictionary_gate(repo),
        _evidence_readiness_gate(repo),
        _source_drift_gate(repo),
        _source_validation_gate(repo),
        _source_contract_gate(repo),
        _github_project_gate(repo),
        _final_handoff_gate(repo),
        _local_gate_status(repo, "uv_build", "release", required=True),
        _local_gate_status(repo, "dashboard_build", "dashboard", required=True),
        _external_gate_status(repo, "pip_audit_strict", "security", required=True),
        _external_gate_status(repo, "npm_audit_dashboard", "security", required=True),
        _external_gate_status(repo, "zizmor_workflow_security", "supply_chain", required=False),
        _external_gate_status(repo, "pixi_available", "toolchain", required=False),
        _external_gate_status(repo, "mojo_available_uv_tool", "toolchain", required=False),
        _workflow_policy_gate(repo),
        _action_pin_gate(repo),
        _sbom_gate(repo),
        _architecture_gate(repo),
        _publication_manifest_gate(repo),
    ]
    summary = summarise_release_gates(gates)
    return ReleaseReadinessReport(gates=tuple(gates), summary=summary)


def summarise_release_gates(gates: list[ReleaseGateRecord]) -> ReleaseReadinessSummary:
    """Summarise release-gate states."""
    statuses: tuple[ReleaseGateStatus, ...] = ("pass", "warn", "fail", "blocked", "missing")
    counts = {status: sum(1 for gate in gates if gate.status == status) for status in statuses}
    required_blocker_count = sum(
        1 for gate in gates if gate.required and gate.status in {"fail", "blocked", "missing"}
    )
    return ReleaseReadinessSummary(
        schema_version="release-readiness-v2",
        gate_count=len(gates),
        pass_count=counts["pass"],
        warn_count=counts["warn"],
        fail_count=counts["fail"],
        blocked_count=counts["blocked"],
        missing_count=counts["missing"],
        required_blocker_count=required_blocker_count,
        repository_release_ready=required_blocker_count == 0,
        research_publication_ready=False,
        osf_registration_ready=False,
        evidence_release_ready=False,
        policy_claims_ready=False,
    )


def write_release_readiness_report(
    report: ReleaseReadinessReport,
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write release-readiness artefacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [gate.as_row() for gate in report.gates]
    jsonl_path = write_jsonl(rows, output_dir / "release_gates.jsonl")
    csv_path = write_csv(rows, output_dir / "release_gates.csv")
    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(report.summary.as_row(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return jsonl_path, csv_path, summary_path


def _local_quality_gate(repo: Path) -> ReleaseGateRecord:
    summary_path = repo / "data" / "derived" / "local_quality_gates" / "summary.json"
    data = _read_json(summary_path)
    if not data:
        return ReleaseGateRecord(
            id="local_quality_profile",
            category="code_quality",
            status="missing",
            required=True,
            evidence="No local quality-gate summary found.",
            recommended_action="Run `reimbursement-atlas local-quality-gates --profile ci`.",
        )
    release_ready = bool(data.get("release_ready"))
    blockers = int(data.get("blocking_failures", 0))
    return ReleaseGateRecord(
        id="local_quality_profile",
        category="code_quality",
        status="pass" if release_ready else "fail",
        required=True,
        evidence=f"profile={data.get('profile')} blocking_failures={blockers}",
        recommended_action="Inspect data/derived/local_quality_gates for failing blocking gates.",
    )


def _local_gate_status(
    repo: Path,
    gate_id: str,
    category: ReleaseGateCategory,
    required: bool,
) -> ReleaseGateRecord:
    row = _find_csv_row(
        repo / "data" / "derived" / "local_quality_gates" / "local_quality_gates.csv",
        "id",
        gate_id,
    )
    if row is None:
        return ReleaseGateRecord(
            id=gate_id,
            category=category,
            status="missing",
            required=required,
            evidence="Gate has not been run in the local quality profile.",
            recommended_action=(
                "Run the local quality-gate profile and regenerate release readiness."
            ),
        )
    outcome = str(row.get("status", ""))
    status = _map_gate_outcome(outcome)
    return ReleaseGateRecord(
        id=gate_id,
        category=category,
        status=status,
        required=required,
        evidence=f"local_quality status={outcome} return_code={row.get('return_code')}",
        recommended_action=_recommendation_for_status(status, gate_id),
    )


def _external_gate_status(
    repo: Path,
    gate_id: str,
    category: ReleaseGateCategory,
    required: bool,
) -> ReleaseGateRecord:
    records = _read_json(repo / "data" / "derived" / "external_quality_gates.json").get(
        "records",
        [],
    )
    matching = [record for record in records if record.get("id") == gate_id]
    if not matching:
        return ReleaseGateRecord(
            id=gate_id,
            category=category,
            status="missing",
            required=required,
            evidence="External gate record is absent.",
            recommended_action="Run scripts/run_external_quality_gates.py.",
        )
    record = matching[0]
    outcome = str(record.get("outcome", ""))
    status = _map_gate_outcome(outcome)
    return ReleaseGateRecord(
        id=gate_id,
        category=category,
        status=status,
        required=required,
        evidence=f"external_quality outcome={outcome} return_code={record.get('return_code')}",
        recommended_action=_recommendation_for_status(status, gate_id),
    )


def _data_dictionary_gate(repo: Path) -> ReleaseGateRecord:
    summary_path = repo / "data" / "derived" / "data_dictionary" / "summary.json"
    data = _read_json(summary_path)
    if not data:
        return ReleaseGateRecord(
            id="data_dictionary_summary",
            category="data_governance",
            status="missing",
            required=True,
            evidence="No data dictionary summary found.",
            recommended_action="Run scripts/make_data_dictionary.py.",
        )
    table_count = int(data.get("table_count", 0))
    return ReleaseGateRecord(
        id="data_dictionary_summary",
        category="data_governance",
        status="pass" if table_count >= 25 else "warn",
        required=True,
        evidence=f"table_count={table_count} total_rows={data.get('total_rows_documented')}",
        recommended_action="Regenerate the data dictionary after publication-manifest changes.",
    )


def _evidence_readiness_gate(repo: Path) -> ReleaseGateRecord:
    summary_path = repo / "data" / "derived" / "evidence_readiness" / "summary.json"
    data = _read_json(summary_path)
    if not data:
        return ReleaseGateRecord(
            id="evidence_readiness_summary",
            category="data_governance",
            status="missing",
            required=True,
            evidence="No evidence-readiness summary found.",
            recommended_action="Run scripts/make_evidence_readiness.py.",
        )
    blocked = int(data.get("blocked", 0))
    return ReleaseGateRecord(
        id="evidence_readiness_summary",
        category="data_governance",
        status="pass" if blocked == 0 else "fail",
        required=True,
        evidence=f"blocked={blocked} prototype_ready={data.get('prototype_ready')}",
        recommended_action="Resolve blocked research questions before evidence release.",
    )


def _source_drift_gate(repo: Path) -> ReleaseGateRecord:
    summary_path = repo / "data" / "derived" / "source_drift" / "summary.json"
    data = _read_json(summary_path)
    if not data:
        return ReleaseGateRecord(
            id="source_drift_summary",
            category="data_governance",
            status="missing",
            required=True,
            evidence="No source/schema drift summary found.",
            recommended_action="Run scripts/make_source_drift_report.py.",
        )
    blockers = int(data.get("blocking_failure_count", 0))
    warnings = int(data.get("warn", 0))
    return ReleaseGateRecord(
        id="source_drift_summary",
        category="data_governance",
        status="pass" if blockers == 0 else "fail",
        required=True,
        evidence=f"blocking_failure_count={blockers} warnings={warnings}",
        recommended_action="Review source drift failures before release.",
    )


def _data_quality_gate(repo: Path) -> ReleaseGateRecord:
    summary = _read_json(repo / "data" / "derived" / "data_quality" / "summary.json")
    if not summary:
        return ReleaseGateRecord(
            id="data_quality_summary",
            category="data_governance",
            status="missing",
            required=True,
            evidence="Data-quality summary missing.",
            recommended_action="Run scripts/make_data_quality_report.py.",
        )
    blockers = int(summary.get("blocking_failures", 0))
    status: ReleaseGateStatus = "pass" if blockers == 0 else "fail"
    return ReleaseGateRecord(
        id="data_quality_summary",
        category="data_governance",
        status=status,
        required=True,
        evidence=f"checks={summary.get('check_count', 0)} blocking_failures={blockers}",
        recommended_action="Resolve blocking data-quality checks before release.",
    )


def _source_validation_gate(repo: Path) -> ReleaseGateRecord:
    summary = _read_json(repo / "data" / "derived" / "source_validation" / "summary.json")
    if not summary:
        return ReleaseGateRecord(
            id="source_content_validation_summary",
            category="data_governance",
            status="missing",
            required=True,
            evidence="Source-content validation summary missing.",
            recommended_action=(
                "Run scripts/make_source_validation.py after download-plan generation."
            ),
        )
    failures = int(summary.get("blocking_failures", 0))
    missing = int(summary.get("missing", 0))
    status: ReleaseGateStatus = "pass" if failures == 0 else "fail"
    if status == "pass" and missing:
        status = "warn"
    return ReleaseGateRecord(
        id="source_content_validation_summary",
        category="data_governance",
        status=status,
        required=True,
        evidence=(
            f"validations={summary.get('validation_count', 0)} "
            f"missing={missing} failures={failures}"
        ),
        recommended_action=(
            "Download missing public files in a network-enabled environment, then rerun validation."
        ),
    )


def _source_contract_gate(repo: Path) -> ReleaseGateRecord:
    summary = _read_json(repo / "data" / "derived" / "source_contracts" / "summary.json")
    if not summary:
        return ReleaseGateRecord(
            id="source_contract_validation_summary",
            category="data_governance",
            status="missing",
            required=True,
            evidence="Source-contract validation summary missing.",
            recommended_action="Run scripts/make_source_contracts.py before reviewed parsing.",
        )
    failures = int(summary.get("blocking_failures", 0))
    missing = int(summary.get("missing", 0))
    status: ReleaseGateStatus = "pass" if failures == 0 else "fail"
    if status == "pass" and missing:
        status = "warn"
    return ReleaseGateRecord(
        id="source_contract_validation_summary",
        category="data_governance",
        status=status,
        required=True,
        evidence=(
            f"contracts={summary.get('contract_count', 0)} missing={missing} failures={failures}"
        ),
        recommended_action="Download sources and rerun contract validation before real parsing.",
    )


def _github_project_gate(repo: Path) -> ReleaseGateRecord:
    summary = _read_json(repo / "data" / "derived" / "github_project" / "summary.json")
    if not summary:
        return ReleaseGateRecord(
            id="github_project_export_summary",
            category="release",
            status="missing",
            required=True,
            evidence="GitHub Project export summary missing.",
            recommended_action="Run scripts/make_github_project_export.py.",
        )
    issue_count = int(summary.get("issue_count", 0))
    return ReleaseGateRecord(
        id="github_project_export_summary",
        category="release",
        status="pass" if issue_count >= 100 else "warn",
        required=True,
        evidence=f"project_items={summary.get('project_item_count', 0)} issue_count={issue_count}",
        recommended_action=(
            "Import generated rows into GitHub Projects once repository credentials exist."
        ),
    )


def _final_handoff_gate(repo: Path) -> ReleaseGateRecord:
    summary = _read_json(repo / "data" / "derived" / "final_handoff" / "summary.json")
    if not summary:
        return ReleaseGateRecord(
            id="final_handoff_summary",
            category="release",
            status="missing",
            required=True,
            evidence="Final handoff summary missing.",
            recommended_action="Run scripts/make_final_handoff.py.",
        )
    return ReleaseGateRecord(
        id="final_handoff_summary",
        category="release",
        status="pass" if summary.get("download_ready") else "warn",
        required=True,
        evidence=(
            f"tasks={summary.get('task_count', 0)} blocked_network="
            f"{summary.get('blocked_network', 0)} blocked_secret="
            f"{summary.get('blocked_secret', 0)}"
        ),
        recommended_action=(
            "Use final_handoff_tasks.csv as the network/credential handoff checklist."
        ),
    )


def _workflow_policy_gate(repo: Path) -> ReleaseGateRecord:
    summary = _read_json(repo / "data" / "derived" / "repo_automation" / "summary.json")
    if not summary:
        return ReleaseGateRecord(
            id="workflow_policy_matrix",
            category="supply_chain",
            status="missing",
            required=True,
            evidence="Workflow policy summary missing.",
            recommended_action="Run scripts/make_repo_automation_matrix.py.",
        )
    fail_count = int(summary.get("fail", 0))
    warn_count = int(summary.get("warn", 0))
    status: ReleaseGateStatus = "pass"
    if fail_count:
        status = "fail"
    elif warn_count:
        status = "warn"
    return ReleaseGateRecord(
        id="workflow_policy_matrix",
        category="supply_chain",
        status=status,
        required=True,
        evidence=f"fail={fail_count} warn={warn_count} pass={summary.get('pass', 0)}",
        recommended_action=(
            "Resolve fail records; gradually burn down warn records before hardened release."
        ),
    )


def _action_pin_gate(repo: Path) -> ReleaseGateRecord:
    plan_path = repo / "data" / "derived" / "repo_automation" / "action_sha_pin_plan.csv"
    unresolved = _csv_row_count(plan_path)
    if unresolved == 0:
        return ReleaseGateRecord(
            id="action_sha_pinning",
            category="supply_chain",
            status="pass",
            required=False,
            evidence="All workflow actions are already SHA-pinned, local, or docker references.",
            recommended_action="Keep action pin resolver in scheduled CI.",
        )
    resolution_path = repo / "data" / "derived" / "repo_automation" / "action_pin_resolution.csv"
    resolved_rows = _csv_rows(resolution_path)
    resolved = sum(1 for row in resolved_rows if row.get("status") == "resolved")
    blocked = sum(1 for row in resolved_rows if row.get("status") == "blocked_network")
    status: ReleaseGateStatus = "warn"
    return ReleaseGateRecord(
        id="action_sha_pinning",
        category="supply_chain",
        status=status,
        required=False,
        evidence=(
            f"unresolved_action_refs={unresolved} resolved={resolved} blocked_network={blocked}"
        ),
        recommended_action=(
            "Resolve tags with network access, review generated suggestions, then pin actions "
            "to immutable SHAs."
        ),
    )


def _sbom_gate(repo: Path) -> ReleaseGateRecord:
    rows = _csv_rows(repo / "data" / "derived" / "sbom" / "sbom_summary.csv")
    component_count = sum(int(row.get("component_count", 0) or 0) for row in rows)
    if len(rows) >= 2 and component_count > 0:
        return ReleaseGateRecord(
            id="sbom_generation",
            category="supply_chain",
            status="pass",
            required=True,
            evidence=f"sbom_count={len(rows)} component_count={component_count}",
            recommended_action="Attach SBOM files to release artefacts and attestations.",
        )
    return ReleaseGateRecord(
        id="sbom_generation",
        category="supply_chain",
        status="missing",
        required=True,
        evidence="SBOM summary is missing or empty.",
        recommended_action="Run scripts/make_sbom.py.",
    )


def _architecture_gate(repo: Path) -> ReleaseGateRecord:
    summary = _read_json(repo / "data" / "derived" / "architecture" / "summary.json")
    if not summary:
        return ReleaseGateRecord(
            id="architecture_boundaries",
            category="architecture",
            status="missing",
            required=True,
            evidence="Architecture summary missing.",
            recommended_action="Run scripts/make_architecture_report.py.",
        )
    violation_count = int(summary.get("layer_violation_count", 0))
    cycle_count = int(summary.get("internal_cycle_count", 0))
    unknown_count = int(summary.get("unknown_layer_count", 0))
    status: ReleaseGateStatus = "pass"
    if violation_count or cycle_count or unknown_count:
        status = "fail"
    return ReleaseGateRecord(
        id="architecture_boundaries",
        category="architecture",
        status=status,
        required=True,
        evidence=(
            f"violations={violation_count} cycles={cycle_count} unknown_layers={unknown_count}"
        ),
        recommended_action=(
            "Fix layer violations, remove cycles, or update the layer map deliberately."
        ),
    )


def _publication_manifest_gate(repo: Path) -> ReleaseGateRecord:
    manifest = _read_json(repo / "data" / "derived" / "publication_manifest.json")
    if not manifest:
        return ReleaseGateRecord(
            id="publication_manifest",
            category="data_governance",
            status="missing",
            required=True,
            evidence="Publication manifest missing.",
            recommended_action="Run scripts/make_publication_manifest.py.",
        )
    warnings = manifest.get("warnings", [])
    artifact_count = int(manifest.get("artifact_count", 0))
    status: ReleaseGateStatus = "pass" if not warnings and artifact_count else "warn"
    return ReleaseGateRecord(
        id="publication_manifest",
        category="data_governance",
        status=status,
        required=True,
        evidence=f"artifact_count={artifact_count} warning_count={len(warnings)}",
        recommended_action="Review licence gates and warnings before publishing derived datasets.",
    )


def _map_gate_outcome(outcome: str) -> ReleaseGateStatus:
    mapping: dict[str, ReleaseGateStatus] = {
        "passed": "pass",
        "failed": "fail",
        "blocked_network": "blocked",
        "missing_tool": "missing",
        "wrong_tool": "fail",
        "timed_out": "fail",
        "skipped": "warn",
    }
    return mapping.get(outcome, "fail")


def _recommendation_for_status(status: ReleaseGateStatus, gate_id: str) -> str:
    if status == "pass":
        return "No action required."
    if status == "blocked":
        return f"Run {gate_id} in a network-enabled CI/local environment."
    if status == "missing":
        return f"Install or generate evidence for {gate_id}."
    if status == "warn":
        return f"Review advisory evidence for {gate_id}."
    return f"Fix {gate_id} before public release."


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _find_csv_row(path: Path, key: str, value: str) -> dict[str, str] | None:
    for row in _csv_rows(path):
        if row.get(key) == value:
            return row
    return None


def _csv_row_count(path: Path) -> int:
    return len(_csv_rows(path))

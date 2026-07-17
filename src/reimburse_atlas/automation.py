"""Repository automation, workflow policy and CI/CD posture helpers."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

WorkflowPinClass = Literal["sha", "major", "minor", "floating", "local", "docker", "unknown"]
PolicyStatus = Literal["pass", "warn", "fail", "not_applicable"]
ControlStatus = Literal["implemented", "partial", "planned", "missing"]

_USES_RE = re.compile(r"^\s*-?\s*uses:\s*['\"]?([^'\"\s#]+)", re.MULTILINE)
_PERMISSIONS_RE = re.compile(r"^permissions:\s*(.*)$", re.MULTILINE)
_CHECKOUT_RE = re.compile(r"uses:\s*actions/checkout@", re.IGNORECASE)
_SHA_RE = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
_MAJOR_TAG_RE = re.compile(r"^v?\d+$")
_MINOR_TAG_RE = re.compile(r"^v?\d+\.\d+(?:\.\d+)?(?:[-+][A-Za-z0-9_.-]+)?$")
_FLOATING_REFS = {"main", "master", "latest", "trunk", "dev", "develop", "HEAD"}


@dataclass(frozen=True)
class WorkflowUseRecord:
    """A GitHub Actions `uses:` reference found in a workflow."""

    workflow: str
    line: int
    uses: str
    action: str
    ref: str
    pin_class: WorkflowPinClass
    is_official_github_action: bool
    policy_status: PolicyStatus
    policy_note: str

    def as_row(self) -> dict[str, object]:
        """Return a CSV/JSON-safe row."""
        return asdict(self)


@dataclass(frozen=True)
class WorkflowPolicyRecord:
    """One workflow policy observation."""

    id: str
    workflow: str
    gate: str
    status: PolicyStatus
    severity: Literal["low", "medium", "high"]
    evidence: str
    recommended_action: str

    def as_row(self) -> dict[str, object]:
        """Return a CSV/JSON-safe row."""
        return asdict(self)


@dataclass(frozen=True)
class AutomationControlRecord:
    """Repository-level CI/CD, security, release or automation control."""

    id: str
    category: str
    status: ControlStatus
    evidence: str
    maturity: Literal["seed", "prototype", "hardened", "advanced"]
    recommended_next_step: str

    def as_row(self) -> dict[str, object]:
        """Return a CSV/JSON-safe row."""
        return asdict(self)


def workflow_files(root: Path) -> list[Path]:
    """Return workflow files relative to the repository root."""
    workflow_dir = root / ".github" / "workflows"
    if not workflow_dir.exists():
        return []
    return sorted(
        path for path in workflow_dir.iterdir() if path.suffix.lower() in {".yml", ".yaml"}
    )


def scan_workflow_uses(root: Path) -> list[WorkflowUseRecord]:
    """Scan workflow `uses:` references and classify pinning posture."""
    records: list[WorkflowUseRecord] = []
    for path in workflow_files(root):
        text = path.read_text(encoding="utf-8")
        for match in _USES_RE.finditer(text):
            uses = match.group(1).strip()
            action, ref = _split_uses_ref(uses)
            pin_class = classify_action_pin(uses)
            policy_status, policy_note = _pin_policy(pin_class)
            records.append(
                WorkflowUseRecord(
                    workflow=_relative(path, root),
                    line=text[: match.start()].count("\n") + 1,
                    uses=uses,
                    action=action,
                    ref=ref,
                    pin_class=pin_class,
                    is_official_github_action=action.startswith(("actions/", "github/")),
                    policy_status=policy_status,
                    policy_note=policy_note,
                )
            )
    return records


def classify_action_pin(uses: str) -> WorkflowPinClass:
    """Classify a GitHub Actions `uses:` reference by pin stability."""
    pin_class: WorkflowPinClass = "unknown"
    if uses.startswith("./"):
        pin_class = "local"
    elif uses.startswith("docker://"):
        pin_class = "docker"
    else:
        _, ref = _split_uses_ref(uses)
        if _SHA_RE.fullmatch(ref):
            pin_class = "sha"
        elif ref in _FLOATING_REFS:
            pin_class = "floating"
        elif _MAJOR_TAG_RE.fullmatch(ref):
            pin_class = "major"
        elif _MINOR_TAG_RE.fullmatch(ref):
            pin_class = "minor"
    return pin_class


def workflow_policy_records(root: Path) -> list[WorkflowPolicyRecord]:
    """Build policy observations for GitHub workflow hardening."""
    records: list[WorkflowPolicyRecord] = []
    uses_records = scan_workflow_uses(root)
    uses_by_workflow: dict[str, list[WorkflowUseRecord]] = {}
    for record in uses_records:
        uses_by_workflow.setdefault(record.workflow, []).append(record)

    for path in workflow_files(root):
        relative = _relative(path, root)
        text = path.read_text(encoding="utf-8")
        records.extend((
            _permissions_record(relative, text),
            _checkout_credentials_record(relative, text),
            _workflow_pin_record(relative, uses_by_workflow.get(relative, [])),
            _trigger_record(relative, text),
        ))
    return sorted(records, key=lambda item: (item.workflow, item.gate, item.id))


def automation_control_records(root: Path) -> list[AutomationControlRecord]:
    """Summarise implemented repo automation and supply-chain controls."""
    workflow_text = _all_workflow_text(root)
    files = {str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()}
    return [
        _control(
            "ci_python_quality",
            "quality",
            "implemented" if "pixi run coverage" in workflow_text else "partial",
            ".github/workflows/ci.yml",
            "hardened",
            "Keep coverage threshold above 90% and add per-module deltas when the codebase grows.",
        ),
        _control(
            "dashboard_build",
            "quality",
            "implemented" if "npm run build" in workflow_text else "partial",
            ".github/workflows/ci.yml",
            "hardened",
            "Add deployment previews when the Hugging Face Space scaffold is activated.",
        ),
        _control(
            "codeql",
            "security",
            "implemented" if "github/codeql-action" in workflow_text else "missing",
            ".github/workflows/security.yml",
            "hardened",
            "Tune CodeQL config as parser/API surfaces mature.",
        ),
        _control(
            "dependency_review",
            "security",
            "implemented" if "dependency-review-action" in workflow_text else "missing",
            ".github/workflows/security.yml",
            "hardened",
            "Block high-severity dependency changes once real-source ingestion begins.",
        ),
        _control(
            "openssf_scorecard",
            "supply_chain",
            "implemented" if "scorecard-action" in workflow_text else "planned",
            ".github/workflows/scorecard.yml",
            "advanced" if "scorecard-action" in workflow_text else "seed",
            "Upload SARIF/code-scanning results for public repositories.",
        ),
        _control(
            "zizmor_workflow_lint",
            "supply_chain",
            "implemented" if "zizmor" in workflow_text else "planned",
            ".github/workflows/workflow-security.yml",
            "advanced" if "zizmor" in workflow_text else "seed",
            "Keep medium-and-higher findings blocking and retain SARIF evidence.",
        ),
        _control(
            "actionlint_workflow_validation",
            "supply_chain",
            "implemented" if "rhysd/actionlint" in workflow_text else "missing",
            ".github/workflows/security-assurance.yml",
            "advanced" if "rhysd/actionlint" in workflow_text else "seed",
            "Keep actionlint SHA-pinned and required by branch protection.",
        ),
        _control(
            "secret_history_scan",
            "security",
            "implemented" if "gitleaks/gitleaks-action" in workflow_text else "missing",
            ".github/workflows/security-assurance.yml",
            "advanced" if "gitleaks/gitleaks-action" in workflow_text else "seed",
            "Retain full-history scanning and rotate any credential before suppressing findings.",
        ),
        _control(
            "reproducible_build_verification",
            "supply_chain",
            "implemented" if "reproducible-build" in workflow_text else "missing",
            ".github/workflows/security-assurance.yml",
            "advanced" if "reproducible-build" in workflow_text else "seed",
            "Require byte-identical wheels and source distributions from the same locked source.",
        ),
        _control(
            "layered_harness_assurance",
            "quality",
            "implemented" if "Harness assurance" in workflow_text else "missing",
            ".github/workflows/harness-assurance.yml",
            "advanced" if "Harness assurance" in workflow_text else "seed",
            "Keep property, integration, E2E and deterministic-regeneration lanes bounded.",
        ),
        _control(
            "artifact_attestations",
            "supply_chain",
            "implemented" if "actions/attest" in workflow_text else "planned",
            ".github/workflows/release.yml",
            "advanced" if "actions/attest" in workflow_text else "prototype",
            "Attest all release bundles and dashboard artefacts.",
        ),
        _control(
            "sbom_generation",
            "supply_chain",
            "implemented"
            if {
                "data/derived/sbom/cyclonedx-python.json",
                "data/derived/sbom/cyclonedx-dashboard.json",
            }.issubset(files)
            else "planned",
            "data/derived/sbom/*.json",
            "advanced"
            if {
                "data/derived/sbom/cyclonedx-python.json",
                "data/derived/sbom/cyclonedx-dashboard.json",
            }.issubset(files)
            else "prototype",
            "Attach SBOMs to releases and archive publication manifests with attestations.",
        ),
        _control(
            "renovate",
            "repo_automation",
            "implemented" if "renovate.json" in files else "missing",
            "renovate.json",
            "hardened",
            "Add automerge rules only after mutation/security gates are stable.",
        ),
        _control(
            "dependabot",
            "repo_automation",
            "implemented" if ".github/dependabot.yml" in files else "missing",
            ".github/dependabot.yml",
            "hardened",
            "Use cooldown and grouping to reduce noisy dependency churn.",
        ),
        _control(
            "data_publication_gates",
            "data_governance",
            "implemented" if "public-data-policy" in workflow_text else "partial",
            "scripts/check_public_data_policy.py",
            "hardened",
            "Add live reviewed-source bundle acceptance tests after first real MBS/CMS ingest.",
        ),
        _control(
            "local_quality_orchestrator",
            "quality",
            "implemented" if "run_local_quality_gates.py" in workflow_text else "partial",
            ".github/workflows/uv-quality.yml",
            "advanced" if "run_local_quality_gates.py" in workflow_text else "prototype",
            "Use the generated evidence bundle as the canonical PR/release validation record.",
        ),
        _control(
            "mutation_nightly",
            "quality",
            "implemented" if "mutmut" in workflow_text else "planned",
            ".github/workflows/mutation-nightly.yml",
            "advanced" if "mutmut" in workflow_text else "prototype",
            "Track mutation score trend rather than using it as a PR blocker initially.",
        ),
        _control(
            "architecture_boundary_gate",
            "architecture",
            "implemented" if "architecture-report" in workflow_text else "planned",
            "scripts/make_architecture_report.py",
            "advanced" if "data/derived/architecture/summary.json" in files else "prototype",
            "Keep layer violations and internal import cycles at zero.",
        ),
        _control(
            "release_readiness_matrix",
            "release",
            "implemented" if "release-readiness" in workflow_text else "planned",
            "scripts/make_release_readiness.py",
            "advanced" if "data/derived/release_readiness/summary.json" in files else "prototype",
            "Treat required release blockers as zero before public release.",
        ),
        _control(
            "issue_forms",
            "repo_automation",
            "implemented" if ".github/ISSUE_TEMPLATE/source-onboarding.yml" in files else "planned",
            ".github/ISSUE_TEMPLATE/*.yml",
            "hardened" if ".github/ISSUE_TEMPLATE/quality-gate.yml" in files else "prototype",
            "Keep source, analysis and quality-gate issues structured for project automation.",
        ),
    ]


def workflow_policy_summary(records: list[WorkflowPolicyRecord]) -> dict[str, int]:
    """Count workflow policy outcomes."""
    summary = {"pass": 0, "warn": 0, "fail": 0, "not_applicable": 0}  # nosec B105
    for record in records:
        summary[record.status] += 1
    return summary


def _split_uses_ref(uses: str) -> tuple[str, str]:
    if "@" not in uses:
        return uses, ""
    action, ref = uses.rsplit("@", 1)
    return action, ref


def _pin_policy(pin_class: WorkflowPinClass) -> tuple[PolicyStatus, str]:
    if pin_class == "sha":
        return "pass", "Action is pinned to a full commit SHA."
    if pin_class in {"local", "docker"}:
        return "not_applicable", f"{pin_class} reference does not use a GitHub action tag."
    if pin_class in {"major", "minor"}:
        return (
            "warn",
            "Tag-pinned action; acceptable for prototype CI, but SHA pinning is preferred.",
        )
    if pin_class == "floating":
        return "fail", "Floating action reference; replace with a pinned tag or commit SHA."
    return "warn", "Unable to classify action pinning; review manually."


def _permissions_record(workflow: str, text: str) -> WorkflowPolicyRecord:
    match = _PERMISSIONS_RE.search(text)
    if match is None:
        return WorkflowPolicyRecord(
            id=f"{_slug(workflow)}__permissions",
            workflow=workflow,
            gate="explicit_permissions",
            status="warn",
            severity="medium",
            evidence="No top-level permissions block detected.",
            recommended_action="Add an explicit least-privilege top-level permissions block.",
        )
    value = match.group(1).strip()
    if value in {"write-all", "read-all"}:
        return WorkflowPolicyRecord(
            id=f"{_slug(workflow)}__permissions",
            workflow=workflow,
            gate="explicit_permissions",
            status="fail" if value == "write-all" else "warn",
            severity="high" if value == "write-all" else "medium",
            evidence=f"Top-level permissions uses {value!r}.",
            recommended_action="Replace broad permissions with job-scoped least privilege.",
        )
    return WorkflowPolicyRecord(
        id=f"{_slug(workflow)}__permissions",
        workflow=workflow,
        gate="explicit_permissions",
        status="pass",
        severity="medium",
        evidence="Top-level permissions block detected.",
        recommended_action="Keep permissions explicit and job-scoped for write operations.",
    )


def _checkout_credentials_record(workflow: str, text: str) -> WorkflowPolicyRecord:
    checkout_count = len(_CHECKOUT_RE.findall(text))
    if checkout_count == 0:
        return WorkflowPolicyRecord(
            id=f"{_slug(workflow)}__checkout_credentials",
            workflow=workflow,
            gate="checkout_persist_credentials_false",
            status="not_applicable",
            severity="low",
            evidence="Workflow does not use actions/checkout.",
            recommended_action="No action required.",
        )
    secure_count = sum(
        1 for block in _checkout_blocks(text) if "persist-credentials: false" in block
    )
    if secure_count == checkout_count:
        return WorkflowPolicyRecord(
            id=f"{_slug(workflow)}__checkout_credentials",
            workflow=workflow,
            gate="checkout_persist_credentials_false",
            status="pass",
            severity="medium",
            evidence=(
                f"{secure_count}/{checkout_count} checkout steps disable credential persistence."
            ),
            recommended_action=(
                "Keep this default unless a write step genuinely needs persisted credentials."
            ),
        )
    return WorkflowPolicyRecord(
        id=f"{_slug(workflow)}__checkout_credentials",
        workflow=workflow,
        gate="checkout_persist_credentials_false",
        status="warn",
        severity="medium",
        evidence=f"{secure_count}/{checkout_count} checkout steps disable credential persistence.",
        recommended_action=(
            "Set `persist-credentials: false` on checkout steps that only need read access."
        ),
    )


def _workflow_pin_record(
    workflow: str,
    uses_records: list[WorkflowUseRecord],
) -> WorkflowPolicyRecord:
    risky = [record for record in uses_records if record.policy_status == "fail"]
    warnings = [record for record in uses_records if record.policy_status == "warn"]
    if risky:
        return WorkflowPolicyRecord(
            id=f"{_slug(workflow)}__action_pinning",
            workflow=workflow,
            gate="action_reference_pinning",
            status="fail",
            severity="high",
            evidence=f"{len(risky)} floating/unclassified action references detected.",
            recommended_action=(
                "Pin workflow actions to exact tags or, preferably, full commit SHAs."
            ),
        )
    if warnings:
        return WorkflowPolicyRecord(
            id=f"{_slug(workflow)}__action_pinning",
            workflow=workflow,
            gate="action_reference_pinning",
            status="warn",
            severity="high",
            evidence=f"{len(warnings)} tag-pinned action references detected; no SHA pins yet.",
            recommended_action="Use Renovate or pin-github-action to migrate action tags to SHAs.",
        )
    return WorkflowPolicyRecord(
        id=f"{_slug(workflow)}__action_pinning",
        workflow=workflow,
        gate="action_reference_pinning",
        status="pass",
        severity="high",
        evidence="All external action references are SHA-pinned or local.",
        recommended_action="Keep action pins updated through automation.",
    )


def _trigger_record(workflow: str, text: str) -> WorkflowPolicyRecord:
    uses_pull_request_target = "pull_request_target:" in text
    if uses_pull_request_target:
        return WorkflowPolicyRecord(
            id=f"{_slug(workflow)}__trigger",
            workflow=workflow,
            gate="unsafe_pull_request_target",
            status="fail",
            severity="high",
            evidence="pull_request_target trigger detected.",
            recommended_action=(
                "Avoid pull_request_target unless the workflow is specifically threat-modelled."
            ),
        )
    return WorkflowPolicyRecord(
        id=f"{_slug(workflow)}__trigger",
        workflow=workflow,
        gate="unsafe_pull_request_target",
        status="pass",
        severity="high",
        evidence="No pull_request_target trigger detected.",
        recommended_action="Keep untrusted pull-request code on read-only pull_request workflows.",
    )


def _checkout_blocks(text: str) -> list[str]:
    lines = text.splitlines()
    blocks: list[str] = []
    for index, line in enumerate(lines):
        if _CHECKOUT_RE.search(line):
            blocks.append("\n".join(lines[index : index + 10]))
    return blocks


def _all_workflow_text(root: Path) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in workflow_files(root))


def _control(
    control_id: str,
    category: str,
    status: ControlStatus,
    evidence: str,
    maturity: Literal["seed", "prototype", "hardened", "advanced"],
    next_step: str,
) -> AutomationControlRecord:
    return AutomationControlRecord(
        id=control_id,
        category=category,
        status=status,
        evidence=evidence,
        maturity=maturity,
        recommended_next_step=next_step,
    )


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")

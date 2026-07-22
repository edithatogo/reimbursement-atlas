"""Final local-download and network-enabled handoff checklist."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, cast

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import FinalHandoffTaskRecord
from reimburse_atlas.registry import project_root

HandoffStatus = Literal[
    "ready_local", "partial", "blocked_network", "blocked_secret", "blocked_review", "complete"
]


def build_final_handoff_tasks(root: Path | None = None) -> list[FinalHandoffTaskRecord]:
    """Build the remaining tasks that require network, credentials or review."""
    repo = root or project_root()
    return [
        FinalHandoffTaskRecord(
            id="final_source_downloads",
            conductor_track="track_live_source_ingestion",
            github_issues=(23, 25, 255),
            task_group="source_ingestion",
            title="Run hardened curl/wget source download plan",
            status=_source_download_status(repo),
            required_environment=(
                "Network-enabled local machine or GitHub runner with outbound HTTPS."
            ),
            command=(
                "PYTHONPATH=src reimbursement-atlas source-download-plan --method curl "
                "&& bash data/derived/source_downloads/download_commands.sh"
            ),
            evidence_path="data/derived/source_downloads/download_attempts.jsonl",
            unblock_condition=(
                "MBS/PBS/CMS source hosts resolve and downloads complete into ignored "
                "data/raw_live storage."
            ),
            recommended_action="Run first, then rerun source-validation and source-contracts.",
            reason_code="source_acquisition_partial",
            gate_evidence=("data/derived/source_downloads/download_attempts.jsonl",),
            external_state="ready",
        ),
        FinalHandoffTaskRecord(
            id="final_mbs_pair_bundle",
            conductor_track="track_live_source_ingestion",
            github_issues=(23,),
            task_group="source_ingestion",
            title="Create reviewed derived-only MBS TXT pair bundle",
            status=(
                "complete"
                if _mbs_pair_bundle_complete(repo)
                else "ready_local"
                if _mbs_pair_available(repo)
                else "blocked_network"
            ),
            required_environment=(
                "Local checkout with downloaded MBS item-map and descriptor TXT files."
            ),
            command=(
                "PYTHONPATH=src reimbursement-atlas reviewed-mbs-txt-pair-bundle "
                "data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT "
                "data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT"
            ),
            evidence_path="data/derived/reviewed_source_bundles/",
            unblock_condition=("Both July 2026 MBS TXT files exist in ignored local raw storage."),
            recommended_action=(
                "Commit only derived rows and redacted provenance after licence review."
            ),
            reason_code=(
                "reviewed_bundle_complete"
                if _mbs_pair_bundle_complete(repo)
                else "reviewed_bundle_pending"
            ),
            gate_evidence=("data/derived/reviewed_source_bundles/",),
            external_state="not_applicable",
        ),
        FinalHandoffTaskRecord(
            id="final_cms_clfs_licence_review",
            conductor_track="track_source_provenance_licence_release",
            github_issues=(24, 492, 496),
            task_group="source_ingestion",
            title="Review CMS CLFS AMA-gated file and derived-field policy",
            status="complete" if _licence_review_complete(repo) else "blocked_review",
            required_environment=(
                "Human review of AMA/CPT licence implications before parsing or publishing fields."
            ),
            command="PYTHONPATH=src reimbursement-atlas source-files",
            evidence_path="docs/LIVE_SOURCE_VALIDATION_PLAYBOOK.md",
            unblock_condition=(
                "Reviewer approves the set of derived CLFS fields that can be stored and published."
            ),
            recommended_action=(
                "Avoid CPT descriptor redistribution; publish payment/metadata only when permitted."
            ),
            reason_code=(
                "checksum_bound_scope_approved"
                if _licence_review_complete(repo)
                else "source_scope_review_pending"
            ),
            gate_evidence=(
                "data/derived/licence_review/licence_review_queue.jsonl",
                "data/licence_review/decisions.jsonl",
                "docs/REVIEW_DECISIONS.md",
            ),
            review_record="data/licence_review/decisions.jsonl",
            external_state="not_applicable",
        ),
        FinalHandoffTaskRecord(
            id="final_pip_audit_strict",
            conductor_track="track_ci_cd_supply_chain",
            github_issues=(191,),
            task_group="security",
            title="Run pip-audit strict in a network-enabled environment",
            status=(
                "complete" if _external_gate_passed(repo, "pip_audit_strict") else "blocked_network"
            ),
            required_environment=(
                "Network-enabled Python environment with access to PyPI advisory APIs."
            ),
            command="uv run --all-extras pip-audit --strict",
            evidence_path="data/derived/external_quality_gates.json",
            unblock_condition=(
                "PyPI advisory lookup completes with no unresolved vulnerabilities."
            ),
            recommended_action="Make this a required release gate in CI before public release.",
            reason_code="external_security_gate",
            gate_evidence=("data/derived/external_quality_gates.json",),
            external_state="not_applicable",
        ),
        FinalHandoffTaskRecord(
            id="final_action_sha_pinning",
            conductor_track="track_ci_cd_supply_chain",
            github_issues=(191,),
            task_group="automation",
            title="Resolve GitHub Action tags to immutable SHAs",
            status=(
                "complete"
                if _external_gate_passed(repo, "repo_automation_matrix")
                and _action_pinning_complete(repo)
                else "blocked_network"
            ),
            required_environment="Network-enabled environment with GitHub API access.",
            command="PYTHONPATH=src python scripts/resolve_action_pins.py",
            evidence_path="data/derived/repo_automation/action_pin_resolution.jsonl",
            unblock_condition=(
                "All action references are resolved and workflows use immutable SHAs "
                "where practical."
            ),
            recommended_action=(
                "Keep all third-party Actions SHA-pinned and zizmor medium findings blocking."
            ),
            reason_code="action_pin_gate",
            gate_evidence=("data/derived/repo_automation/action_pin_resolution.jsonl",),
            external_state="not_applicable",
        ),
        FinalHandoffTaskRecord(
            id="final_hf_dataset_space",
            conductor_track="track_publication_hf_spaces",
            github_issues=(534,),
            task_group="publication",
            title="Publish gated Hugging Face dataset and Space dry run",
            status="ready_local" if _publication_ready(repo) else "blocked_review",
            required_environment=(
                "GitHub Actions with configured HF_TOKEN, HF_DATASET_REPO and HF_SPACE_REPO "
                "targets, plus licence and evidence review."
            ),
            command="gh workflow run huggingface.yml",
            evidence_path=".github/workflows/huggingface.yml",
            unblock_condition=(
                "Licence, evidence, policy and research gates pass and publication is explicitly "
                "approved."
            ),
            recommended_action=(
                "The dry run has passed; inspect the candidate bundle and publish only after "
                "the remaining review gates are approved."
            ),
            reason_code=(
                "publication_candidate_ready"
                if _publication_ready(repo)
                else "publication_review_pending"
            ),
            gate_evidence=(
                "data/derived/release_readiness/summary.json",
                "data/derived/publication_manifest/summary.json",
            ),
            external_state="ready" if _publication_ready(repo) else "pending",
        ),
        FinalHandoffTaskRecord(
            id="final_osf_protocol_pack",
            conductor_track="track_osf_registration_record_quality",
            github_issues=(484, 488, 511),
            task_group="research",
            title="Create OSF protocol/report components and upload preregistration pack",
            status="ready_local" if _osf_review_approved(repo) else "blocked_review",
            required_environment=(
                "Configured OSF personal access token and private project, plus approved "
                "protocol text."
            ),
            command="gh workflow run osf.yml",
            evidence_path="data/derived/osf/osf_publication_manifest.json",
            unblock_condition=(
                "Protocols, licence, methods and governance decisions are human-reviewed and "
                "the sync manifest rows are explicitly approved."
            ),
            recommended_action=(
                "The private project and token-gated plan are configured; keep upload fail-closed "
                "until the reviewed preregistration decision is recorded."
            ),
            reason_code=(
                "osf_registration_review_approved"
                if _osf_review_approved(repo)
                else "osf_registration_review_pending"
            ),
            gate_evidence=(
                "data/derived/osf/registration_freeze.json",
                "data/derived/osf/osf_publication_manifest.json",
            ),
            review_record="data/derived/osf/registration_freeze.json",
            external_state="ready" if _osf_review_approved(repo) else "pending",
        ),
        FinalHandoffTaskRecord(
            id="final_osf_registration_drift_check",
            conductor_track="track_osf_registration_record_quality",
            github_issues=(484, 489, 511),
            task_group="research",
            title="Verify OSF registration fingerprint and amendment state",
            status=(
                "ready_local"
                if _osf_review_approved(repo) and _osf_snapshot_available(repo)
                else "blocked_review"
            ),
            required_environment=(
                "Approved protocol freeze, human methods/licence/governance review and an "
                "exported OSF registration metadata snapshot."
            ),
            command=(
                "PYTHONPATH=src reimbursement-atlas osf-registration-check "
                '--remote-state-path "$OSF_REGISTRATION_SNAPSHOT"'
            ),
            evidence_path="data/derived/osf/registration_freeze.json",
            unblock_condition=(
                "The reviewed freeze is approved, an active OSF registration snapshot is "
                "exported, and protocol/manifest fingerprints match without mutation."
            ),
            recommended_action=(
                "Run the check before any upload or amendment; treat drift as a new review "
                "decision rather than overwriting the registered state."
            ),
            reason_code=(
                "osf_registration_snapshot_ready"
                if _osf_review_approved(repo) and _osf_snapshot_available(repo)
                else "osf_registration_snapshot_pending"
            ),
            gate_evidence=("data/derived/osf/registration_freeze.json",),
            review_record="data/derived/osf/registration_freeze.json",
            external_state="pending",
        ),
        FinalHandoffTaskRecord(
            id="final_mapping_calibration_review",
            conductor_track="track_evidence_adjudication_review",
            github_issues=(490, 491),
            task_group="mappings",
            title="Adjudicate mapping gold standards and negative controls",
            status="complete" if _mapping_evaluation_accepted(repo) else "blocked_review",
            required_environment="Human domain review of the synthetic mapping calibration cases.",
            command="pixi run mapping-calibration",
            evidence_path="data/derived/vertical_slice/mapping_calibration_gate.json",
            unblock_condition=(
                "Reviewer confirms the positive/negative control outcomes and approves the "
                "mapping threshold for the intended research question."
            ),
            recommended_action=(
                "Do not use the current calibration precision/specificity as evidence-grade "
                "performance; resolve the two triggered negative controls first."
            ),
            reason_code=(
                "mapping_holdout_accepted"
                if _mapping_evaluation_accepted(repo)
                else "mapping_adjudication_pending"
            ),
            gate_evidence=(
                "data/derived/vertical_slice/mapping_review_pack_plan.json",
                "data/derived/vertical_slice/mapping_calibration_gate.json",
            ),
            external_state="not_applicable",
        ),
        FinalHandoffTaskRecord(
            id="final_historical_source_expansion",
            conductor_track="track_historical_source_archival_reproducibility",
            github_issues=(255, 486, 492),
            task_group="source_ingestion",
            title="Review historical MBS/PBS source expansion and licence scope",
            status="complete" if _historical_review_complete(repo) else "blocked_review",
            required_environment=(
                "Human source/licence review plus network access to historical MBS and "
                "PBS releases."
            ),
            command=(
                "pixi run historical-sources && pixi run source-download-plan && "
                "pixi run source-contracts"
            ),
            evidence_path="data/derived/historical_sources/summary.json",
            unblock_condition=(
                "Historical release URLs, reuse terms and a reviewed PBS extract are approved "
                "for derived-only processing; the metadata-only archive inventory is already "
                "generated."
            ),
            recommended_action=(
                "Keep historical pages and unreviewed PBS extracts metadata-only; do not infer "
                "temporal evidence from missing releases. The current archive inventory covers "
                "343 targets across 32 pages, but no raw historical payloads are approved."
            ),
            reason_code=(
                "historical_source_review_complete"
                if _historical_review_complete(repo)
                else "historical_source_review_pending"
            ),
            gate_evidence=("data/derived/historical_sources/summary.json",),
            external_state="not_applicable",
        ),
        FinalHandoffTaskRecord(
            id="final_dashboard_visual_review",
            conductor_track="track_public_product_citation_dashboard",
            github_issues=(493, 501),
            task_group="release",
            title="Review cross-platform dashboard visual baselines",
            status="complete" if _dashboard_review_approved(repo) else "blocked_review",
            required_environment=(
                "Human visual review across the supported browser/OS matrix with approved "
                "baselines."
            ),
            command="cd apps/dashboard && npm run test:browser",
            evidence_path="docs/DASHBOARD_VALIDATION.md",
            unblock_condition=(
                "Reviewed screenshots or platform-specific baselines are approved without "
                "accessibility, layout or provenance regressions."
            ),
            recommended_action=(
                "Use the existing 9-route browser smoke suite as the pre-review gate; do not "
                "treat a single macOS rendering as cross-platform proof."
            ),
            reason_code=(
                "dashboard_human_review_approved"
                if _dashboard_review_approved(repo)
                else "dashboard_human_review_pending"
            ),
            gate_evidence=(
                "docs/DASHBOARD_VALIDATION.md",
                "data/derived/dashboard_review/automated_review_packet.json",
            ),
            review_record="data/derived/dashboard_review/human_review.json",
            external_state="not_applicable",
        ),
        FinalHandoffTaskRecord(
            id="final_release_candidate",
            conductor_track="track_release_record_archive_maturity",
            github_issues=(487, 507),
            task_group="release",
            title="Generate final release-readiness report and public archive",
            status="ready_local" if _publication_ready(repo) else "blocked_review",
            required_environment=(
                "Network-enabled runner after source/security/publication gates complete."
            ),
            command=(
                "PYTHONPATH=src reimbursement-atlas release-readiness && "
                "PYTHONPATH=src reimbursement-atlas data-quality"
            ),
            evidence_path="data/derived/release_readiness/summary.json",
            unblock_condition=(
                "Required software blockers are zero and repository_release_ready is true. "
                "Research, evidence and policy-claim readiness remain separate fail-closed gates."
            ),
            recommended_action=(
                "Only then cut a signed, attested public release and archive to Zenodo/OSF."
            ),
            reason_code=(
                "external_release_candidate_ready"
                if _publication_ready(repo)
                else "external_release_review_pending"
            ),
            gate_evidence=("data/derived/release_readiness/summary.json",),
            external_state="ready" if _publication_ready(repo) else "pending",
        ),
    ]


def write_final_handoff_tasks(
    rows: list[FinalHandoffTaskRecord],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write final handoff checklist rows and summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    data = [row.model_dump(mode="json") for row in rows]
    jsonl_path = write_jsonl(data, output_dir / "final_handoff_tasks.jsonl")
    csv_path = write_csv(data, output_dir / "final_handoff_tasks.csv")
    summary = {
        "task_count": len(rows),
        "ready_local": sum(row.status == "ready_local" for row in rows),
        "partial": sum(row.status == "partial" for row in rows),
        "blocked_network": sum(row.status == "blocked_network" for row in rows),
        "blocked_secret": sum(row.status == "blocked_secret" for row in rows),
        "blocked_review": sum(row.status == "blocked_review" for row in rows),
        "complete": sum(row.status == "complete" for row in rows),
        "download_ready": True,
        "download_ready_note": (
            "Repo archive is ready; remaining tasks require network, credentials, or "
            "human licence/research review."
        ),
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return jsonl_path, csv_path, summary_path


def _mbs_pair_available(repo: Path) -> bool:
    raw = repo / "data" / "raw_live" / "au_mbs"
    if (raw / "20260701_MBSONLINE_IMAP.TXT").is_file() and (
        raw / "20260701_MBSONLINE_DESC.TXT"
    ).is_file():
        return True
    bundles = repo / "data" / "derived" / "reviewed_source_bundles"
    return any(
        (bundle / "validation_report.json").is_file()
        for bundle in bundles.glob("bundle_au_mbs_20260701_txt_pair_*/")
    )


def _licence_review_complete(repo: Path) -> bool:
    """Return true when every current checksum-bound queue row is approved."""
    queue = _read_jsonl(repo / "data/derived/licence_review/licence_review_queue.jsonl")
    decisions = _read_jsonl(repo / "data/licence_review/decisions.jsonl")
    approved = {
        (row.get("review_id"), row.get("relative_path"), row.get("checksum_sha256"))
        for row in decisions
        if row.get("decision") == "approved"
    }
    required = {
        (row.get("review_id"), row.get("relative_path"), row.get("checksum_sha256"))
        for row in queue
    }
    return bool(required) and required <= approved


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        return []
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            return []
        if not isinstance(value, dict):
            return []
        rows.append(cast("dict[str, object]", value))
    return rows


def _publication_ready(repo: Path) -> bool:
    summary = _read_json(repo / "data/derived/release_readiness/summary.json")
    return all(
        summary.get(key) is True
        for key in (
            "repository_release_ready",
            "research_publication_ready",
            "evidence_release_ready",
            "policy_claims_ready",
        )
    )


def _osf_review_approved(repo: Path) -> bool:
    freeze = _read_json(repo / "data/derived/osf/registration_freeze.json")
    return (
        freeze.get("review_approved") is True
        and freeze.get("source_cutoff_status") == "approved"
        and freeze.get("source_cutoff") not in {None, "not-frozen"}
    )


def _osf_snapshot_available(repo: Path) -> bool:
    snapshot = _read_json(repo / "data/derived/osf/remote_registration_snapshot.json")
    return bool(snapshot.get("registration_id")) and snapshot.get("status") in {
        "draft",
        "registered",
        "embargoed",
    }


def _mapping_evaluation_accepted(repo: Path) -> bool:
    evaluation = _read_json(repo / "data/derived/mapping_study/evaluation_summary.json")
    return evaluation.get("status") == "accepted" and evaluation.get("evaluated_once") is True


def _historical_review_complete(repo: Path) -> bool:
    summary = _read_json(repo / "data/derived/historical_sources/summary.json")
    return summary.get("review_queue_status") == "approved" and summary.get("status") in {
        "reviewed_complete",
        "derived_processing_approved",
    }


def _dashboard_review_approved(repo: Path) -> bool:
    review = _read_json(repo / "data/derived/dashboard_review/human_review.json")
    raw_scope = review.get("scope")
    scope = cast("dict[str, object]", raw_scope) if isinstance(raw_scope, dict) else {}
    return (
        review.get("status") == "approved_within_scope"
        and bool(review.get("reviewed_at"))
        and scope.get("provenance") is True
    )


def _read_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return cast("dict[str, object]", value) if isinstance(value, dict) else {}


def _mbs_pair_bundle_complete(repo: Path) -> bool:
    """Confirm that the derived MBS pair review packet was actually generated."""
    bundles = repo / "data" / "derived" / "reviewed_source_bundles"
    for bundle in bundles.glob("bundle_au_mbs_20260701_txt_pair_*/"):
        report_path = bundle / "validation_report.json"
        summary_path = bundle / "summary.json"
        records_path = bundle / "au_mbs_20260701_txt_pair_schedule_items.jsonl"
        if not (report_path.is_file() and summary_path.is_file() and records_path.is_file()):
            continue
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if (
            report.get("parse_success") is True
            and report.get("raw_files_copied_to_bundle") is False
            and report.get("review_required_before_publication") is True
            and summary.get("fail") == 0
            and summary.get("missing") == 0
        ):
            return True
    return False


def _action_pinning_complete(repo: Path) -> bool:
    plan = repo / "data" / "derived" / "repo_automation" / "action_sha_pin_plan.csv"
    if not plan.is_file():
        return False
    return len(plan.read_text(encoding="utf-8").splitlines()) <= 1


def _source_download_status(repo: Path) -> HandoffStatus:
    """Classify acquisition progress without treating a partial run as complete."""
    plans = repo / "data" / "derived" / "source_downloads" / "download_plans.jsonl"
    attempts = repo / "data" / "derived" / "source_downloads" / "download_attempts.jsonl"
    if not plans.is_file() or not attempts.is_file():
        return "complete" if _mbs_pair_available(repo) else "blocked_network"
    planned = [
        json.loads(line) for line in plans.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    acquired = {
        (record.get("source_file_id"), record.get("target_path"))
        for record in (
            json.loads(line)
            for line in attempts.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
        if record.get("status") == "downloaded"
    }
    executable = {
        (record.get("source_file_id"), record.get("target_path"))
        for record in planned
        if record.get("should_execute") is True
    }
    statuses = {
        record.get("status")
        for record in (
            json.loads(line)
            for line in attempts.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    if executable and executable <= acquired and statuses <= {"downloaded"}:
        return "complete"
    return "partial" if acquired else "blocked_network"


def _external_gate_passed(repo: Path, gate_id: str) -> bool:
    """Read a passed external gate without treating stale handoff text as evidence."""
    path = repo / "data" / "derived" / "external_quality_gates.json"
    if not path.is_file():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return any(
        record.get("id") == gate_id and record.get("outcome") == "passed"
        for record in payload.get("records", [])
    )

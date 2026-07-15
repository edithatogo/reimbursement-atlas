"""Final local-download and network-enabled handoff checklist."""

from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import FinalHandoffTaskRecord
from reimburse_atlas.registry import project_root


def build_final_handoff_tasks(root: Path | None = None) -> list[FinalHandoffTaskRecord]:
    """Build the remaining tasks that require network, credentials or review."""
    repo = root or project_root()
    return [
        FinalHandoffTaskRecord(
            id="final_source_downloads",
            task_group="source_ingestion",
            title="Run hardened curl/wget source download plan",
            status="complete" if _source_downloads_complete(repo) else "blocked_network",
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
        ),
        FinalHandoffTaskRecord(
            id="final_mbs_pair_bundle",
            task_group="source_ingestion",
            title="Create reviewed derived-only MBS TXT pair bundle",
            status="ready_local" if _mbs_pair_available(repo) else "blocked_network",
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
        ),
        FinalHandoffTaskRecord(
            id="final_cms_clfs_licence_review",
            task_group="source_ingestion",
            title="Review CMS CLFS AMA-gated file and derived-field policy",
            status="blocked_review",
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
        ),
        FinalHandoffTaskRecord(
            id="final_pip_audit_strict",
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
        ),
        FinalHandoffTaskRecord(
            id="final_action_sha_pinning",
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
        ),
        FinalHandoffTaskRecord(
            id="final_hf_dataset_space",
            task_group="publication",
            title="Publish gated Hugging Face dataset and Space dry run",
            status="blocked_secret",
            required_environment=(
                "GitHub Actions with HF_TOKEN, HF_DATASET_REPO and HF_SPACE_REPO secrets."
            ),
            command="gh workflow run huggingface.yml",
            evidence_path=".github/workflows/huggingface.yml",
            unblock_condition=(
                "Secrets are configured and publication manifest has no raw-source warnings."
            ),
            recommended_action=(
                "Run as a dry release first; inspect dataset card and Space build logs."
            ),
        ),
        FinalHandoffTaskRecord(
            id="final_osf_protocol_pack",
            task_group="research",
            title="Create OSF protocol/report components and upload preregistration pack",
            status="blocked_secret",
            required_environment="OSF personal access token and approved protocol text.",
            command="gh workflow run osf.yml",
            evidence_path="data/derived/osf/osf_publication_manifest.json",
            unblock_condition=("Protocols are human-reviewed and OSF credentials are configured."),
            recommended_action=(
                "Treat OSF upload as preregistration candidate, not final publication, "
                "until approved."
            ),
        ),
        FinalHandoffTaskRecord(
            id="final_osf_registration_drift_check",
            task_group="research",
            title="Verify OSF registration fingerprint and amendment state",
            status="blocked_review",
            required_environment=(
                "Approved protocol freeze, human methods/licence/governance review and an "
                "exported OSF registration metadata snapshot."
            ),
            command=(
                "PYTHONPATH=src reimbursement-atlas osf-registration-check "
                "--remote-state-path /path/to/registration_snapshot.json"
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
        ),
        FinalHandoffTaskRecord(
            id="final_mapping_calibration_review",
            task_group="mappings",
            title="Adjudicate mapping gold standards and negative controls",
            status="blocked_review",
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
        ),
        FinalHandoffTaskRecord(
            id="final_historical_source_expansion",
            task_group="source_ingestion",
            title="Review historical MBS/PBS source expansion and licence scope",
            status="blocked_review",
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
        ),
        FinalHandoffTaskRecord(
            id="final_dashboard_visual_review",
            task_group="release",
            title="Review cross-platform dashboard visual baselines",
            status="blocked_review",
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
        ),
        FinalHandoffTaskRecord(
            id="final_release_candidate",
            task_group="release",
            title="Generate final release-readiness report and public archive",
            status="blocked_review",
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


def _action_pinning_complete(repo: Path) -> bool:
    plan = repo / "data" / "derived" / "repo_automation" / "action_sha_pin_plan.csv"
    if not plan.is_file():
        return False
    return len(plan.read_text(encoding="utf-8").splitlines()) <= 1


def _source_downloads_complete(repo: Path) -> bool:
    """Return true when acquisition evidence or a reviewed source bundle exists."""
    attempts = repo / "data" / "derived" / "source_downloads" / "download_attempts.jsonl"
    if attempts.is_file():
        for line in attempts.read_text(encoding="utf-8").splitlines():
            if '"status": "downloaded"' in line:
                return True
    return _mbs_pair_available(repo)


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

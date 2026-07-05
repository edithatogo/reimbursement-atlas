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
            status="blocked_network",
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
            status="blocked_network",
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
            status="blocked_network",
            required_environment="Network-enabled environment with GitHub API access.",
            command="PYTHONPATH=src python scripts/resolve_action_pins.py",
            evidence_path="data/derived/repo_automation/action_pin_resolution.jsonl",
            unblock_condition=(
                "All action references are resolved and workflows use immutable SHAs "
                "where practical."
            ),
            recommended_action=("After SHA pinning, make zizmor blocking rather than advisory."),
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
            unblock_condition=("Required blocker count is zero and public_release_ready is true."),
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
    return (raw / "20260701_MBSONLINE_IMAP.TXT").is_file() and (
        raw / "20260701_MBSONLINE_DESC.TXT"
    ).is_file()

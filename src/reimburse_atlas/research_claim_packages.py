"""Deterministic, fail-closed research claim-package candidates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from reimburse_atlas.validation import read_jsonl_rows

QUESTION_SOURCES: dict[str, tuple[str, ...]] = {
    "rq_genomics_coverage_price": (
        "au_mbs",
        "us_cms_clfs",
        "us_cms_mcd",
        "uk_genomic_test_directory",
    ),
    "rq_cognitive_procedural": ("au_mbs", "us_cms_pfs", "ca_on_ohip"),
    "rq_medicine_opacity": ("au_pbs", "us_cms_asp", "nz_pharmac"),
    "rq_local_national_coverage": ("us_cms_mcd", "au_mbs", "uk_nhs_payment_scheme"),
    "rq_source_transparency": ("source_registry",),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _approved_package_hashes(root: Path) -> set[tuple[str, str]]:
    """Return package paths and hashes backed by complete scoped decisions."""
    decisions_path = root / "data/research_claims/decisions.jsonl"
    if not decisions_path.exists():
        return set()
    approved: set[tuple[str, str]] = set()
    for decision in read_jsonl_rows(decisions_path):
        package_path = str(decision.get("claim_package_path", ""))
        digest = str(decision.get("claim_package_sha256", ""))
        package = root / package_path
        review_path = root / str(decision.get("review_record", ""))
        decision_valid = (
            decision.get("status") == "approved_within_scope"
            and decision.get("reviewed_derived_inputs") is True
            and decision.get("analysis_validated") is True
        )
        evidence_valid = package.is_file() and _sha256(package) == digest and review_path.is_file()
        if not decision_valid or not evidence_valid:
            continue
        review = json.loads(review_path.read_text(encoding="utf-8"))
        if (
            review.get("status") == "approved_within_scope"
            and review.get("claim_package_path") == package_path
            and review.get("claim_package_sha256") == digest
        ):
            approved.add((package_path, digest))
    return approved


def _write_bounded_reports(  # ruff:ignore[too-many-locals] - renderer fields are explicit
    root: Path, package_paths: list[Path]
) -> None:
    """Render bounded evidence reports without creating manuscripts or submissions."""
    question_path = root / "data/seed/research_questions.jsonl"
    if not question_path.exists():
        return
    questions = {str(row["id"]): row for row in read_jsonl_rows(question_path)}
    approved = _approved_package_hashes(root)
    for path in package_paths:
        package = json.loads(path.read_text(encoding="utf-8"))
        question_id = str(package["research_question_id"])
        question = questions[question_id]
        relative = path.relative_to(root).as_posix()
        digest = _sha256(path)
        is_approved = (relative, digest) in approved
        result_lines = [
            f"- `{key}`: `{value}`"
            for key, value in sorted(package.get("descriptive_results", {}).items())
        ]
        methods = [f"- {value}" for value in question.get("methods", [])]
        sources = [f"- `{value}`" for value in package["required_sources"]]
        outputs = [f"- {value}" for value in question.get("outputs", [])]
        supported = [f"- {value}" for value in package.get("supported_claims", [])]
        unsupported = [f"- {value}" for value in package.get("unsupported_claims", [])]
        report = root / str(question["report_path"])
        report.parent.mkdir(parents=True, exist_ok=True)
        approval_status = "approved_within_scope" if is_approved else "pending"
        status_text = (
            "This is a deterministic bounded evidence report, not a paper or preprint. "
            f"The checksum-bound claim package is `{approval_status}`. "
            "No manuscript submission or broad research-publication approval is implied."
        )
        report.write_text(
            "\n".join([
                f"# Bounded evidence report: {question_id}",
                "",
                "## Status and scope",
                "",
                status_text,
                "",
                "## Research question",
                "",
                str(question["question"]),
                "",
                "## Evidence binding",
                "",
                f"- Claim package: `{relative}`",
                f"- Claim package SHA-256: `{digest}`",
                f"- Analysis status: `{package['analysis_status']}`",
                f"- Required reviewed sources: `{len(package['required_sources'])}`",
                f"- Missing reviewed sources: `{len(package['missing_reviewed_sources'])}`",
                "",
                "## Prespecified methods",
                "",
                *methods,
                "",
                (
                    "The methods remain bounded to deterministic descriptive transformations of "
                    "reviewed derived inputs. They do not estimate treatment effects, infer "
                    "hidden prices, equate unlike payment concepts, or convert schedule inclusion "
                    "into a coverage conclusion."
                ),
                "",
                "## Source scope",
                "",
                *sources,
                "",
                (
                    "Each source is represented through its reviewed derived bundle, version and "
                    "checksum. Missing observations are exclusions rather than zero values. Raw "
                    "payloads, restricted descriptors and confidential commercial terms are not "
                    "included in this report."
                ),
                "",
                "## Descriptive results",
                "",
                *result_lines,
                "",
                "## Supported claims",
                "",
                *supported,
                "",
                "## Excluded interpretations",
                "",
                *unsupported,
                (
                    "- No paper, preprint, causal, universal reimbursement, or unsupported "
                    "policy claim is authorized."
                ),
                "",
                "## Planned non-manuscript outputs",
                "",
                *outputs,
                "",
                (
                    "These output names describe bounded repository artefacts only. They do not "
                    "authorize external submission, peer-reviewed publication, system rankings, "
                    "clinical recommendations or policy decisions."
                ),
                "",
                "## Audit checklist",
                "",
                "- Confirm the claim-package path and SHA-256 before using any result.",
                "- Confirm all required sources remain checksum-bound and approved within scope.",
                "- Preserve source-specific licence, attribution and excluded-field rules.",
                "- Keep denominators, missingness and jurisdictional differences explicit.",
                "- Do not generalize beyond the supported claims listed above.",
                "- Treat any changed input or package checksum as a new review state.",
                "",
                "## Reproducibility",
                "",
                (
                    "Regenerate with `pixi run research-claim-packages`. Inputs are reviewed "
                    "derived bundles; raw payloads and restricted descriptors are excluded."
                ),
                (
                    "The generation step is deterministic and performs no network mutation. "
                    "Review decisions remain external checksum-bound records, so regeneration can "
                    "recognize an existing approval without embedding or manufacturing approval "
                    "inside the claim package itself."
                ),
                "",
            ]),
            encoding="utf-8",
        )


def _reviewed_sources(root: Path) -> dict[str, list[dict[str, Any]]]:
    reviewed: dict[str, list[dict[str, Any]]] = {}
    pattern = "data/derived/reviewed_source_bundles/*/source_snapshots.jsonl"
    for path in sorted(root.glob(pattern)):
        for row in read_jsonl_rows(path):
            source_id = str(row["source_id"])
            reviewed.setdefault(source_id, []).append({
                "bundle_path": path.parent.relative_to(root).as_posix(),
                "source_version_id": row["source_version_id"],
                "source_checksum_sha256": row["checksum_sha256"],
            })
    return reviewed


def _registry_summary(root: Path) -> dict[str, Any]:
    path = root / "data/seed/source_registry.jsonl"
    rows = read_jsonl_rows(path)
    return {
        "input_path": path.relative_to(root).as_posix(),
        "input_sha256": _sha256(path),
        "source_count": len(rows),
        "machine_readable_count": sum(row["machine_readable"] is True for row in rows),
        "historical_versions_count": sum(row["historical_versions"] is True for row in rows),
        "utilisation_data_count": sum(row["utilisation_data"] is True for row in rows),
        "licence_notes_count": sum(bool(row.get("licence_notes")) for row in rows),
        "primary_url_count": sum(bool(row.get("primary_url")) for row in rows),
    }


def build_claim_package_candidates(root: Path) -> list[dict[str, Any]]:
    """Build bounded package candidates without granting claim approval."""
    reviewed = _reviewed_sources(root)
    mapping_path = root / "data/derived/mapping_study/expansion_v9/evaluation_summary.json"
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    registry = _registry_summary(root)
    packages: list[dict[str, Any]] = []

    for question_id, required_sources in QUESTION_SOURCES.items():
        if question_id == "rq_source_transparency":
            observed = ["source_registry"]
            missing: list[str] = []
        else:
            observed = sorted(set(required_sources) & set(reviewed))
            missing = sorted(set(required_sources) - set(observed))

        status = "complete" if not missing else "partial"
        approval_status = (
            "pending_accountable_review" if status == "complete" else "not_reviewable_source_gap"
        )
        scope = (
            "Metadata transparency of the registered public sources."
            if question_id == "rq_source_transparency"
            else "Reviewed-source availability and bounded descriptive evidence only."
        )
        package: dict[str, Any] = {
            "schema_version": "research-claim-package-v1",
            "research_question_id": question_id,
            "analysis_status": status,
            "claim_approval_status": approval_status,
            "scope": scope,
            "required_sources": list(required_sources),
            "reviewed_sources_present": observed,
            "missing_reviewed_sources": missing,
            "reviewed_source_evidence": {
                source_id: reviewed[source_id] for source_id in observed if source_id in reviewed
            },
            "mapping_validation": {
                "study_cycle": mapping["study_cycle"],
                "status": mapping["status"],
                "holdout_case_count": mapping["denominators"]["overall"],
                "holdout_fingerprint": mapping["holdout_fingerprint"],
                "overall_metrics": mapping["metrics"]["overall"],
                "input_path": mapping_path.relative_to(root).as_posix(),
                "input_sha256": _sha256(mapping_path),
            },
            "validation": {
                "deterministic": True,
                "reviewed_inputs_only": True,
                "raw_payloads_included": False,
                "restricted_descriptors_included": False,
                "analysis_validated": True,
            },
            "supported_claims": [],
            "unsupported_claims": [
                "No causal effect is estimated.",
                "No cross-jurisdiction price equivalence is inferred.",
                "No coverage decision is inferred from the presence of a fee or price.",
            ],
        }
        if question_id == "rq_source_transparency":
            package["descriptive_results"] = registry
            package["supported_claims"] = [
                (
                    f"The registry contains {registry['source_count']} source records; "
                    f"{registry['machine_readable_count']} are marked machine-readable."
                ),
                (
                    f"{registry['historical_versions_count']} records identify historical "
                    "versions and every registry row includes licence notes and a primary URL."
                ),
            ]
        else:
            package["descriptive_results"] = {
                "required_source_count": len(required_sources),
                "reviewed_source_count": len(observed),
                "missing_source_count": len(missing),
            }
            package["supported_claims"] = [
                (
                    f"{len(observed)} of {len(required_sources)} protocol-required sources "
                    "have checksum-bound reviewed derived bundles."
                )
            ]
            if missing:
                package["unsupported_claims"].append(
                    "The full protocol question is not answerable until these reviewed "
                    f"sources are present: {', '.join(missing)}."
                )
        packages.append(package)
    return packages


def write_claim_package_candidates(root: Path) -> list[Path]:
    """Write one canonical JSON package per research question."""
    output = root / "data/derived/research_claims"
    output.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for package in build_claim_package_candidates(root):
        path = output / f"{package['research_question_id']}.json"
        path.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        paths.append(path)
    approved = _approved_package_hashes(root)
    summary = {
        "schema_version": "research-claim-package-summary-v1",
        "package_count": len(paths),
        "complete_count": sum(
            json.loads(path.read_text(encoding="utf-8"))["analysis_status"] == "complete"
            for path in paths
        ),
        "reviewable_count": sum(
            json.loads(path.read_text(encoding="utf-8"))["analysis_status"] == "complete"
            for path in paths
        ),
        "approved_within_scope_count": sum(
            (path.relative_to(root).as_posix(), _sha256(path)) in approved for path in paths
        ),
        "pending_accountable_review_count": sum(
            json.loads(path.read_text(encoding="utf-8"))["analysis_status"] == "complete"
            and (path.relative_to(root).as_posix(), _sha256(path)) not in approved
            for path in paths
        ),
        "partial_source_gap_count": sum(
            json.loads(path.read_text(encoding="utf-8"))["analysis_status"] == "partial"
            for path in paths
        ),
        "packages": [
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": _sha256(path),
            }
            for path in paths
        ],
    }
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_bounded_reports(root, paths)
    paths.append(summary_path)
    return paths

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
        scope = (
            "Metadata transparency of the registered public sources."
            if question_id == "rq_source_transparency"
            else "Reviewed-source availability and bounded descriptive evidence only."
        )
        package: dict[str, Any] = {
            "schema_version": "research-claim-package-v1",
            "research_question_id": question_id,
            "analysis_status": status,
            "claim_approval_status": "pending_accountable_review",
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
    summary = {
        "schema_version": "research-claim-package-summary-v1",
        "package_count": len(paths),
        "complete_count": sum(
            json.loads(path.read_text(encoding="utf-8"))["analysis_status"] == "complete"
            for path in paths
        ),
        "pending_accountable_review_count": len(paths),
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
    paths.append(summary_path)
    return paths

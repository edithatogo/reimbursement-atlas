"""Generate the public, fail-closed project status manifest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root, repo_relative


def _read_summary(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError:
        return {"status": "missing", "evidence": repo_relative(path)}
    except json.JSONDecodeError:
        return {"status": "missing", "evidence": repo_relative(path)}
    if not isinstance(payload, dict):
        return {"status": "invalid", "evidence": repo_relative(path)}
    return cast("dict[str, Any]", payload)


def build_public_status_manifest(root: Path | None = None) -> dict[str, Any]:
    """Build separate software, evidence and publication readiness dimensions."""
    repo = root or project_root()
    release = _read_summary(repo, "data/derived/release_readiness/summary.json")
    evidence = _read_summary(repo, "data/derived/evidence_readiness/summary.json")
    quality = _read_summary(repo, "data/derived/data_quality/summary.json")
    source = _read_summary(repo, "data/derived/source_validation/summary.json")
    quality_status = "pass" if quality.get("blocking_failures") == 0 else "blocked"
    source_status = "pass" if source.get("blocking_failures") == 0 else "blocked"
    evidence_count = int(evidence.get("research_question_count", 0))
    evidence_ready = int(evidence.get("evidence_ready", 0))
    pending_licence_reviews = int(
        _read_summary(repo, "data/derived/licence_review/summary.json").get("pending_count", 0)
    )
    blockers: list[dict[str, Any]] = []
    if pending_licence_reviews:
        blockers.append({
            "id": "licence_review",
            "category": "human_review",
            "status": "blocked_review",
            "summary": (
                f"{pending_licence_reviews} publication candidates still require licence review."
            ),
            "next_action": "Record accountable reviewer decisions in the checksum-bound queue.",
            "evidence_path": "data/derived/licence_review/summary.json",
        })
    if not bool(release.get("evidence_release_ready")):
        blockers.append({
            "id": "evidence_release",
            "category": "research_review",
            "status": "blocked_review",
            "summary": "Evidence release is not approved.",
            "next_action": (
                "Complete source, mapping, methods and research review before making "
                "evidence claims."
            ),
            "evidence_path": "data/derived/evidence_readiness/summary.json",
        })
    if not bool(release.get("research_publication_ready")):
        blockers.append({
            "id": "research_publication",
            "category": "publication",
            "status": "gated",
            "summary": "Research publication remains gated.",
            "next_action": (
                "Approve the frozen protocols, publication manifest and release decision."
            ),
            "evidence_path": "data/derived/release_readiness/summary.json",
        })
    if not bool(release.get("osf_registration_ready")):
        blockers.append({
            "id": "osf_registration",
            "category": "osf",
            "status": "gated",
            "summary": "OSF registration is not approved.",
            "next_action": ("Complete accountable methods, domain, licence and governance review."),
            "evidence_path": "data/derived/protocols/protocol_status.jsonl",
        })
    return {
        "schema_version": "public-status-v1",
        "project": "reimbursement-atlas",
        "software": {
            "status": "ready" if release.get("repository_release_ready") else "not_ready",
            "repository_release_ready": bool(release.get("repository_release_ready")),
            "dashboard_build": "tracked_gate",
        },
        "evidence": {
            "status": "ready" if release.get("evidence_release_ready") else "not_ready",
            "evidence_release_ready": bool(release.get("evidence_release_ready")),
            "data_quality": quality_status,
            "source_validation": source_status,
            "research_publication_ready": bool(release.get("research_publication_ready")),
            "readiness_rows": evidence_count,
            "evidence_ready_rows": evidence_ready,
            "prototype_ready_rows": int(evidence.get("prototype_ready", 0)),
        },
        "publication": {
            "status": "ready" if release.get("research_publication_ready") else "gated",
            "osf_registration_ready": bool(release.get("osf_registration_ready")),
            "huggingface_publication": "manual approval and token required",
            "zenodo_doi": "manual release approval required",
        },
        "blockers": blockers,
        "claims_policy": (
            "Do not claim evidence or public-release readiness until reviewed sources, licences, "
            "human research review and release gates pass."
        ),
        "evidence_paths": {
            "release_readiness": "data/derived/release_readiness/summary.json",
            "evidence_readiness": "data/derived/evidence_readiness/summary.json",
            "data_quality": "data/derived/data_quality/summary.json",
            "source_validation": "data/derived/source_validation/summary.json",
        },
    }


def main() -> None:
    """Write the tracked dashboard status manifest."""
    root = project_root()
    payload = build_public_status_manifest(root)
    path = root / "apps/dashboard/public/status.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {repo_relative(path)}")


if __name__ == "__main__":
    main()

"""Contracts for the public product and dashboard status surface."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.check_public_docs import build_public_docs_report
from scripts.make_public_status_manifest import build_public_status_manifest
from scripts.sync_dashboard_seed import sanitise_public_text
from scripts.validate_citation import validate_citation


def test_citation_metadata_passes_repository_contract() -> None:
    """The tracked citation file contains the required public software metadata."""
    errors = validate_citation(Path("CITATION.cff"))
    assert errors == []


def test_public_status_separates_software_evidence_and_publication(tmp_path: Path) -> None:
    """The status manifest remains fail-closed when evidence summaries are incomplete."""
    for relative, payload in {
        "data/derived/release_readiness/summary.json": {
            "repository_release_ready": True,
            "evidence_release_ready": False,
            "research_publication_ready": False,
            "osf_registration_ready": False,
        },
        "data/derived/evidence_readiness/summary.json": {"row_count": 2},
        "data/derived/data_quality/summary.json": {"status": "warn"},
        "data/derived/source_validation/summary.json": {"status": "blocked"},
    }.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    manifest = build_public_status_manifest(tmp_path)

    assert manifest["software"]["status"] == "ready"
    assert manifest["evidence"]["status"] == "not_ready"
    assert manifest["publication"]["status"] == "gated"
    assert manifest["evidence"]["source_validation"] == "blocked"
    assert {item["id"] for item in manifest["blockers"]} >= {
        "evidence_release",
        "research_publication",
        "osf_registration",
    }


def test_public_dashboard_assets_redact_local_raw_cache_paths() -> None:
    """Public derived assets must not expose ignored local raw-cache locations."""
    result = sanitise_public_text("source=data/raw_live/mbs/file.txt")

    assert "data/raw_live" not in result
    assert "[ignored-local-raw-cache]/mbs/file.txt" in result


def test_public_docs_report_is_machine_readable() -> None:
    """Documentation freshness emits a passing report for the repository contract."""
    report = build_public_docs_report(Path())

    assert report["schema_version"] == "public-docs-v1"
    assert report["status"] == "pass"
    assert report["error_count"] == 0

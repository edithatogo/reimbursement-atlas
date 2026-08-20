from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.archive_publication import REQUIRED_READY_FLAGS

ROOT = Path(__file__).parents[2]


def test_osf_network_workflows_are_retired() -> None:
    assert not (ROOT / ".github/workflows/osf.yml").exists()
    assert not (ROOT / ".github/workflows/osf-registration-monitor.yml").exists()


def test_active_publication_contracts_do_not_depend_on_osf() -> None:
    assert "osf_registration_ready" not in REQUIRED_READY_FLAGS
    for relative in (
        "src/reimburse_atlas/release_readiness.py",
        "src/reimburse_atlas/archive_publication.py",
        "scripts/check_huggingface_publication_gates.py",
        "scripts/make_public_status_manifest.py",
    ):
        assert "osf_registration_ready" not in (ROOT / relative).read_text(encoding="utf-8")


def test_historical_osf_registration_evidence_is_preserved() -> None:
    for relative in (
        "data/derived/osf/remote_registration_receipt.json",
        "data/derived/osf/remote_registration_snapshot.json",
        "data/derived/osf/registration_freeze.json",
        "data/osf_review/registration_decision.json",
        "data/osf_review/post_registration_evolution.json",
        "docs/OSF_DEPRECATION.md",
    ):
        assert (ROOT / relative).is_file()


def test_historical_osf_plan_is_not_an_active_seed_lake_table() -> None:
    """Deprecated OSF planning evidence must not be exported as current product data."""
    manifest = json.loads(
        (ROOT / "data/derived/seed_lake/manifest.json").read_text(encoding="utf-8")
    )
    assert "osf_component_plan" not in {row["name"] for row in manifest["tables"]}

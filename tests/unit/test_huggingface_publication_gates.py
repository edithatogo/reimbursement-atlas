from __future__ import annotations

import json
from pathlib import Path

from scripts.check_huggingface_bundle import validate_bundle
from scripts.check_huggingface_destination import destination_report
from scripts.check_huggingface_publication_gates import publication_gate_failures


def _write(root: Path, relative: str, value: dict[str, object]) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _write_bundle_files(root: Path, *, dataset_card: str) -> None:
    (root / "infra/huggingface").mkdir(parents=True, exist_ok=True)
    (root / "apps/dashboard/dist").mkdir(parents=True, exist_ok=True)
    (root / "infra/huggingface/DATASET_CARD.md").write_text(dataset_card, encoding="utf-8")
    (root / "infra/huggingface/README.md").write_text("dataset", encoding="utf-8")
    (root / "infra/huggingface/SPACE_README.md").write_text(
        "sdk: static\nlicense: apache-2.0\nraw restricted source\n", encoding="utf-8"
    )
    (root / "data/derived").mkdir(parents=True, exist_ok=True)
    (root / "data/derived/publication_manifest.json").write_text("{}", encoding="utf-8")
    (root / "apps/dashboard/dist/index.html").write_text("<html></html>", encoding="utf-8")
    (root / "apps/dashboard/dist/status.json").write_text("{}", encoding="utf-8")


def test_huggingface_bundle_requires_mixed_data_license_disclosure(tmp_path: Path) -> None:
    _write_bundle_files(tmp_path, dataset_card="# Dataset\n")

    errors = validate_bundle(tmp_path)

    assert any("DATASET_CARD.md missing marker" in error for error in errors)


def test_huggingface_bundle_accepts_governed_dataset_card(tmp_path: Path) -> None:
    _write_bundle_files(
        tmp_path,
        dataset_card=(
            "license: other\n"
            "pretty_name: Reimbursement Atlas\n"
            "Source-specific licensing applies.\n"
            "This does not grant Apache-2.0 rights to underlying data.\n"
            "Publish only manifest rows with confirmed redistribution permission.\n"
        ),
    )

    assert validate_bundle(tmp_path) == []


def test_huggingface_destination_report_is_read_only_and_detects_drift() -> None:
    """The live destination contract records metadata only and flags mismatches."""
    payloads = {
        "https://huggingface.co/api/datasets/owner/dataset": {
            "id": "owner/dataset",
            "cardData": {"license": "other"},
        },
        "https://huggingface.co/api/spaces/owner/space": {
            "id": "owner/space",
            "cardData": {"license": "mit", "sdk": "gradio"},
        },
    }

    def fetcher(url: str):
        return payloads[url], None

    report = destination_report("owner/dataset", "owner/space", fetcher)

    assert report["mutation_performed"] is False
    assert report["targets"]["dataset"]["status"] == "pass"
    assert report["targets"]["space"]["status"] == "drift"
    assert report["targets"]["space"]["remediation"]
    assert report["remediation_plan"]["dataset"] == []
    assert any("static" in item for item in report["remediation_plan"]["space"])
    assert report["status"] == "drift"
    assert "raw" not in json.dumps(report).lower()


def test_huggingface_destination_fetch_error_only_recommends_retry() -> None:
    def fetcher(_url: str):
        return {}, "temporary outage"

    report = destination_report("owner/dataset", "owner/space", fetcher)

    assert report["status"] == "drift"
    assert report["targets"]["dataset"]["reachable"] is False
    assert report["targets"]["space"]["remediation"] == [
        "Retry the read-only metadata check after the endpoint is reachable."
    ]


def test_publication_gates_fail_closed_for_review_candidate(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "data/derived/release_readiness/summary.json",
        {
            "repository_release_ready": True,
            "research_publication_ready": False,
            "evidence_release_ready": False,
            "policy_claims_ready": False,
        },
    )
    _write(
        tmp_path, "data/derived/protocols/summary.json", {"protocol_count": 1, "osf_ready_count": 0}
    )
    _write(tmp_path, "data/derived/source_contracts/summary.json", {"fail": 0, "missing": 1})
    _write(tmp_path, "data/derived/data_quality/summary.json", {"fail": 0, "missing": 0})
    _write(
        tmp_path,
        "data/derived/publication_manifest.json",
        {"artifacts": [{"relative_path": "seed.csv", "licence_gate": "public_reuse_review"}]},
    )

    failures = publication_gate_failures(tmp_path)

    assert failures
    assert any("licence review" in failure for failure in failures)
    assert any("OSF-ready" in failure for failure in failures)


def test_publication_gates_pass_for_explicitly_approved_manifest(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "data/derived/release_readiness/summary.json",
        {
            "repository_release_ready": True,
            "research_publication_ready": True,
            "evidence_release_ready": True,
            "policy_claims_ready": True,
        },
    )
    _write(
        tmp_path, "data/derived/protocols/summary.json", {"protocol_count": 1, "osf_ready_count": 1}
    )
    _write(tmp_path, "data/derived/source_contracts/summary.json", {"fail": 0, "missing": 0})
    _write(tmp_path, "data/derived/data_quality/summary.json", {"fail": 0, "missing": 0})
    _write(
        tmp_path,
        "data/derived/publication_manifest.json",
        {
            "artifacts": [
                {
                    "relative_path": "seed.csv",
                    "licence_gate": "permissive_candidate",
                    "contains_raw_source_payload": False,
                }
            ]
        },
    )

    assert publication_gate_failures(tmp_path) == []

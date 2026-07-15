from __future__ import annotations

import json
from pathlib import Path

from scripts.check_huggingface_publication_gates import publication_gate_failures


def _write(root: Path, relative: str, value: dict[str, object]) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


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

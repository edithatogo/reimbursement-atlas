"""Operational churn is automatic; source/field/rights expansion is not."""

import hashlib
import json
from pathlib import Path

import pytest

from reimburse_atlas.publication import build_publication_manifest
from reimburse_atlas.standing_approval import metadata_scope_valid, standing_policy
from scripts.reconcile_licence_decisions import reconcile


@pytest.mark.parametrize("suffix", [".json", ".jsonl", ".csv"])
def test_metadata_renewal_and_boundaries(tmp_path: Path, suffix: str) -> None:
    path = Path(f"data/derived/receipt{suffix}")
    (tmp_path / path).parent.mkdir(parents=True)
    rights = tmp_path / "rights.md"
    rights.write_text("Permitted metadata only.")
    policy = {
        "schema_version": "standing-approval-v1",
        "rights_files": {"rights.md": hashlib.sha256(rights.read_bytes()).hexdigest()},
        "metadata": {
            str(path): {
                "fields": ["source_id", "count"],
                "risk_values": {"source_id": ['"pbs"']},
            }
        },
    }
    policy_path = tmp_path / "data/licence_review/standing_scope.json"
    policy_path.parent.mkdir(parents=True)
    policy_path.write_text(json.dumps(policy))
    for count in (1, 50):
        (tmp_path / path).write_text(
            f"source_id,count\npbs,{count}\n"
            if suffix == ".csv"
            else json.dumps({"source_id": "pbs", "count": count}) + "\n"
        )
        assert metadata_scope_valid(tmp_path, str(path))
        artifact = build_publication_manifest((path,), root=tmp_path).artifacts[0]
        assert artifact.approval_requirement == "automatic_policy"
        assert artifact.licence_gate == "permissive_candidate"
    assert not metadata_scope_valid(tmp_path, "data/raw_live/pbs.pdf")
    ledger = tmp_path / "data/licence_review/decisions.jsonl"
    ledger.write_text(
        json.dumps({
            "relative_path": str(path),
            "checksum_sha256": hashlib.sha256((tmp_path / path).read_bytes()).hexdigest(),
            "decision": "approved",
            "reviewer": "standing-scope-policy",
        })
        + "\n"
    )
    queue = tmp_path / "data/derived/licence_review/licence_review_queue.jsonl"
    queue.parent.mkdir(parents=True)
    queue.write_text(
        json.dumps({
            "relative_path": str(path),
            "checksum_sha256": hashlib.sha256((tmp_path / path).read_bytes()).hexdigest(),
            "review_id": "test_receipt",
        })
        + "\n"
    )
    assert reconcile(tmp_path) == 1
    assert reconcile(tmp_path) == 0
    rights.write_text("Rights changed")
    assert reconcile(tmp_path) == 1
    assert json.loads(ledger.read_text())["decision"] == "blocked"
    artifact = build_publication_manifest((path,), root=tmp_path).artifacts[0]
    assert artifact.licence_gate == "public_reuse_review"
    rights.write_text("Permitted metadata only.")
    if suffix != ".csv":
        for value in ({"descriptor": "restricted"}, [{"raw": "payload"}]):
            (tmp_path / path).write_text(json.dumps({"source_id": "pbs", "count": value}))
            assert not metadata_scope_valid(tmp_path, str(path))
    (tmp_path / path).write_text('{"source_id":"new_provider","count":1}')
    assert not metadata_scope_valid(tmp_path, str(path))
    (tmp_path / path).write_text('{"source_id":"pbs","count":1,"descriptor":"restricted"}')
    assert not metadata_scope_valid(tmp_path, str(path))
    rights.write_text("Rights changed")
    assert not metadata_scope_valid(tmp_path, str(path))
    policy_path.write_text("malformed")
    assert standing_policy(tmp_path) == {}


@pytest.mark.parametrize("value", [None, [], {"schema_version": "unknown"}])
def test_invalid_policy_grants_nothing(tmp_path: Path, value: object) -> None:
    assert standing_policy(tmp_path) == {}
    path = tmp_path / "data/licence_review/standing_scope.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(value))
    assert standing_policy(tmp_path) == {}

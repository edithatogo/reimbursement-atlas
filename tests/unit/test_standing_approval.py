"""Operational churn is automatic; source/field/rights expansion is not."""

import hashlib
import json
from pathlib import Path

import pytest

from reimburse_atlas.dashboard_review import (
    EXPECTED_PROJECTS,
    EXPECTED_ROUTES,
    dashboard_renewal_delegated,
)
from reimburse_atlas.final_handoff import build_final_handoff_tasks
from reimburse_atlas.publication import build_publication_manifest
from reimburse_atlas.standing_approval import (
    metadata_content_valid,
    metadata_scope_valid,
    standing_policy,
)
from scripts.reconcile_licence_decisions import reconcile


@pytest.mark.parametrize(
    "value", ["/Users/private/data", "token=secret", "restricted descriptor", "raw payload"]
)
def test_unapproved_free_text_cannot_renew(value: str) -> None:
    scope = json.dumps({
        "fields": ["source_id", "notes"],
        "risk_values": {"source_id": ['"pbs"']},
        "string_sha256": {"notes": [hashlib.sha256(b"Approved metadata").hexdigest()]},
    })
    assert metadata_content_valid(
        json.dumps({"source_id": "pbs", "notes": "Approved metadata"}), ".json", scope
    )
    assert not metadata_content_valid(
        json.dumps({"source_id": "pbs", "notes": value}), ".json", scope
    )


def test_duplicate_csv_headers_cannot_hide_content() -> None:
    scope = json.dumps({"fields": ["source_id", "count"], "risk_values": {"source_id": ['"pbs"']}})
    assert not metadata_content_valid(
        "source_id,source_id,count\nrestricted,pbs,1\n", ".csv", scope
    )


def test_duplicate_json_keys_cannot_hide_content() -> None:
    scope = json.dumps({"fields": ["source_id", "count"], "risk_values": {"source_id": ['"pbs"']}})
    assert not metadata_content_valid(
        '{"source_id":"restricted","source_id":"pbs","count":1}', ".json", scope
    )


@pytest.mark.parametrize("timestamp", ["2026-08-30T00:00:00Z", "2026-02-30T00:00:00Z"])
def test_typed_renewal_and_status_names(timestamp: str) -> None:
    row = {
        "source_id": "pbs",
        "checksum_sha256": "a" * 64,
        "generated_at": timestamp,
        "status_counts": {"downloaded": 3},
        "notes": ["Approved metadata"],
    }
    scope = json.dumps({
        "fields": list(row),
        "risk_values": {"source_id": ['"pbs"']},
        "string_sha256": {
            "status_counts": [hashlib.sha256(b"downloaded").hexdigest()],
            "notes": [hashlib.sha256(b"Approved metadata").hexdigest()],
        },
    })
    assert metadata_content_valid(json.dumps(row), ".json", scope) == timestamp.startswith(
        "2026-08"
    )
    row["status_counts"] = {"restricted descriptor": 3}
    assert not metadata_content_valid(json.dumps(row), ".json", scope)


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


def test_delegated_machine_failure_is_not_an_owner_review_request(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def not_ready(_root: Path) -> bool:
        return False

    def delegated(_root: Path) -> bool:
        return True

    monkeypatch.setattr("reimburse_atlas.final_handoff._dashboard_review_approved", not_ready)
    monkeypatch.setattr("reimburse_atlas.final_handoff.dashboard_renewal_delegated", delegated)
    rows = build_final_handoff_tasks(tmp_path)
    row = next(row for row in rows if row.id == "final_dashboard_visual_review")
    assert row.status == "partial"
    assert row.reason_code == "dashboard_automated_evidence_refresh_required"


@pytest.mark.parametrize(
    "case", ["valid", "routes", "projects", "malformed", "non_object", "missing"]
)
def test_dashboard_delegation_preserves_scope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
) -> None:
    human = {
        "status": "approved_within_scope",
        "scope": {"routes": list(EXPECTED_ROUTES)},
        "automated_packet_sha256": "a" * 64,
        "owner_packet_sha256": "b" * 64,
    }
    human_path = tmp_path / "data/derived/dashboard_review/human_review.json"
    human_path.parent.mkdir(parents=True)
    human_path.write_text(json.dumps(human))
    policy_path = tmp_path / "data/licence_review/standing_scope.json"
    policy_path.parent.mkdir(parents=True)
    policy_path.write_text(
        json.dumps({
            "schema_version": "standing-approval-v1",
            "dashboard": {
                "renew_with_passing_automation": True,
                "automated_packet_sha256": "a" * 64,
                "owner_packet_sha256": "b" * 64,
            },
        })
    )
    reviewed = json.dumps({
        "routes": [] if case == "routes" else list(EXPECTED_ROUTES),
        "projects": [] if case == "projects" else list(EXPECTED_PROJECTS),
    }).encode()
    if case == "malformed":
        reviewed = b"invalid"
    elif case == "non_object":
        reviewed = b"[]"

    def snapshot(_repo: Path, _human: dict[str, object]) -> tuple[str, bytes, bytes] | None:
        return None if case == "missing" else ("c" * 40, reviewed, b"{}")

    monkeypatch.setattr("reimburse_atlas.dashboard_review._approved_packet_bytes", snapshot)
    assert dashboard_renewal_delegated(tmp_path) is (case == "valid")

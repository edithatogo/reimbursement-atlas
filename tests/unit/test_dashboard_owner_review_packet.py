from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from reimburse_atlas.dashboard_review import (
    _json_at_commit,  # ruff:ignore[import-private-name] - fail-closed helper branches need direct coverage.
    _standing_approval_valid,  # ruff:ignore[import-private-name] - see above.
    dashboard_data_fingerprint,
    dashboard_review_evidence,
    dashboard_source_fingerprint,
    normalize_csv_receipt,
    normalize_public_status_dashboard_receipt,
    resolve_repo_head,
)
from scripts.make_dashboard_owner_review_packet import PROVENANCE_INPUTS, build_packet
from scripts.make_dashboard_review_packet import PROJECTS, ROUTES
from scripts.make_public_status_manifest import build_public_status_manifest


def _write_json(root: Path, relative: str, value: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _machine_ready_root(tmp_path: Path) -> Path:
    commit = "a" * 40
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git/HEAD").write_text(commit, encoding="utf-8")
    _write_json(
        tmp_path,
        "data/derived/dashboard_review/automated_review_packet.json",
        {
            "status": "pass",
            "tested_commit": commit,
            "coverage_complete": True,
            "routes": list(ROUTES),
            "projects": list(PROJECTS),
            "test_count": 64,
            "screenshots": [
                {"route": route, "project": project} for route in ROUTES for project in PROJECTS
            ],
            "workflow": {
                "workflow": "Dashboard browser matrix",
                "run_id": "123",
                "run_attempt": "1",
                "artifact_name": "dashboard-browser-review-123",
                "workflow_url": "https://github.com/owner/repo/actions/runs/123",
            },
        },
    )
    _write_json(
        tmp_path,
        "data/derived/source_validation/summary.json",
        {"status": "pass", "blocking_failures": 0},
    )
    _write_json(tmp_path, "data/derived/evidence_readiness/summary.json", {})
    _write_json(
        tmp_path,
        "data/derived/release_readiness/summary.json",
        {
            "evidence_release_ready": False,
            "repository_release_ready": True,
            "research_publication_ready": False,
        },
    )
    _write_json(tmp_path, "data/derived/publication_manifest.json", {"status": "gated"})
    _write_json(
        tmp_path,
        "apps/dashboard/public/status.json",
        build_public_status_manifest(tmp_path),
    )
    automated_path = tmp_path / "data/derived/dashboard_review/automated_review_packet.json"
    automated = json.loads(automated_path.read_text(encoding="utf-8"))
    automated["source_fingerprint"] = dashboard_source_fingerprint(tmp_path)
    automated["data_fingerprint"] = dashboard_data_fingerprint(tmp_path)
    automated_path.write_text(json.dumps(automated), encoding="utf-8")
    return tmp_path


def test_owner_packet_is_machine_ready_but_does_not_imply_human_approval(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    packet = build_packet(_machine_ready_root(tmp_path))

    assert packet["status"] == "pending_accountable_review"
    assert packet["commit_parity"] is True
    assert packet["route_coverage_bounded"] is True
    assert packet["screenshot_count"] == 44
    assert all(row["status"] == "pass" for row in packet["provenance_assertions"])
    assert packet["prohibited_content_check"]["status"] == "pass"
    assert "approved_within_scope" in packet["accountable_checklist"][-1]
    _write_json(
        tmp_path,
        "data/licence_review/standing_scope.json",
        {
            "schema_version": "standing-approval-v1",
            "dashboard": {"renew_with_passing_automation": True},
        },
    )
    assert build_packet(tmp_path)["status"] == "pending_standing_scope_validation"


def test_owner_packet_blocks_prohibited_public_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    root = _machine_ready_root(tmp_path)
    (root / "apps/dashboard/public/leak.txt").write_text(
        "source=/Users/example/data/raw_live/payload.csv",
        encoding="utf-8",
    )

    packet = build_packet(root)

    assert packet["status"] == "automated_evidence_blocked"
    check = packet["prohibited_content_check"]
    assert check["status"] == "fail"
    assert {row["rule"] for row in check["findings"]} == {
        "local_absolute_path",
        "raw_live_path",
    }


def test_current_owner_packet_is_ready_for_bounded_accountable_review() -> None:
    packet = build_packet(Path.cwd())

    assert packet["status"] in {
        "pending_accountable_review",
        "pending_standing_scope_validation",
        "automated_evidence_blocked",
    }
    assert packet["routes"] == list(ROUTES)
    assert packet["screenshot_count"] == 44
    assert packet["automated_test_count"] == 64
    assert len(packet["provenance_inputs"]) >= 4


def test_dashboard_evidence_serializes_stable_evidence_commit(tmp_path: Path) -> None:
    automated = tmp_path / "data/derived/dashboard_review/automated_review_packet.json"
    automated.parent.mkdir(parents=True)
    automated.write_text(
        json.dumps({
            "tested_commit": "a" * 40,
            "source_fingerprint": dashboard_source_fingerprint(tmp_path),
            "data_fingerprint": dashboard_data_fingerprint(tmp_path),
        }),
        encoding="utf-8",
    )
    git = tmp_path / ".git"
    git.mkdir()
    (git / "HEAD").write_text("b" * 40, encoding="utf-8")

    evidence = dashboard_review_evidence(tmp_path)

    assert evidence["head"] == "a" * 40
    assert evidence["checks"]["head_parity"] is False


def test_dashboard_evidence_invalidates_changed_displayed_data(tmp_path: Path) -> None:
    root = _machine_ready_root(tmp_path)
    displayed = root / "apps/dashboard/public/data/source_registry.csv"
    displayed.parent.mkdir(parents=True, exist_ok=True)
    displayed.write_text("id,status\na,ready\n", encoding="utf-8")
    owner = build_packet(root)
    owner_path = root / "data/derived/dashboard_review/owner_review_packet.json"
    owner_path.parent.mkdir(parents=True, exist_ok=True)
    owner_path.write_text(json.dumps(owner), encoding="utf-8")
    displayed.write_text("id,status\na,changed\n", encoding="utf-8")

    evidence = dashboard_review_evidence(root)

    assert evidence["checks"]["displayed_data_parity"] is False


def test_dashboard_source_fingerprint_normalizes_exact_osf_deprecation_copy(
    tmp_path: Path,
) -> None:
    component = tmp_path / "apps/dashboard/src/components/StatusOverview.astro"
    component.parent.mkdir(parents=True)
    component.write_text("OSF, Hugging Face and DOI gates", encoding="utf-8")
    reviewed = dashboard_source_fingerprint(tmp_path)

    component.write_text("Hugging Face, Zenodo and DOI gates", encoding="utf-8")
    assert dashboard_source_fingerprint(tmp_path) == reviewed

    component.write_text("Hugging Face and DOI gates", encoding="utf-8")
    assert dashboard_source_fingerprint(tmp_path) != reviewed


def test_dashboard_source_fingerprint_normalizes_exact_protocol_field_rename(
    tmp_path: Path,
) -> None:
    page = tmp_path / "apps/dashboard/src/pages/roadmap/index.astro"
    page.parent.mkdir(parents=True)
    page.write_text('const field = "osf_ready";', encoding="utf-8")
    reviewed = dashboard_source_fingerprint(tmp_path)

    page.write_text('const field = "protocol_ready";', encoding="utf-8")
    assert dashboard_source_fingerprint(tmp_path) == reviewed

    page.write_text('const field = "publication_ready";', encoding="utf-8")
    assert dashboard_source_fingerprint(tmp_path) != reviewed


def test_dashboard_evidence_reuses_integrity_checked_standing_approval(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Routine data refreshes do not require another bounded visual approval."""
    root = _machine_ready_root(tmp_path)
    current_automated_path = root / "data/derived/dashboard_review/automated_review_packet.json"
    current_automated = json.loads(current_automated_path.read_text(encoding="utf-8"))
    current_owner = build_packet(root)
    owner_path = root / "data/derived/dashboard_review/owner_review_packet.json"
    owner_path.write_text(json.dumps(current_owner), encoding="utf-8")

    reviewed_commit = "b" * 40
    reviewed_automated = dict(current_automated)
    reviewed_automated["tested_commit"] = reviewed_commit
    reviewed_automated["data_fingerprint"] = "1" * 64
    reviewed_automated["screenshot_count"] = 44
    reviewed_owner = dict(current_owner)
    reviewed_owner["tested_commit"] = reviewed_commit
    reviewed_owner["current_head"] = reviewed_commit
    reviewed_owner["data_fingerprint"] = "1" * 64
    historical = {
        "data/derived/dashboard_review/automated_review_packet.json": json.dumps(
            reviewed_automated
        ).encode(),
        "data/derived/dashboard_review/owner_review_packet.json": json.dumps(
            reviewed_owner
        ).encode(),
    }
    human = {
        "status": "approved_within_scope",
        "reviewed_at": "2026-08-20T00:00:00Z",
        "reviewer": "repository-owner",
        "commit": reviewed_commit,
        "automated_packet_sha256": hashlib.sha256(
            historical["data/derived/dashboard_review/automated_review_packet.json"]
        ).hexdigest(),
        "owner_packet_sha256": hashlib.sha256(
            historical["data/derived/dashboard_review/owner_review_packet.json"]
        ).hexdigest(),
        "scope": {"routes": list(ROUTES)},
    }
    _write_json(root, "data/derived/dashboard_review/human_review.json", human)

    def historical_file(_repo: Path, commit: str, path: Path) -> bytes | None:
        if commit != reviewed_commit:
            return None
        return historical.get(path.as_posix())

    monkeypatch.setattr("reimburse_atlas.dashboard_review._git_file_at_commit", historical_file)

    evidence = dashboard_review_evidence(root)

    assert evidence["approval_mode"] == "standing_scoped"
    assert evidence["checks"]["displayed_data_parity"] is True
    assert evidence["checks"]["human_scoped_approval"] is True
    assert evidence["checks"]["packet_hash_parity"] is True


def test_dashboard_standing_approval_resolves_later_receipt_commit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The approval receipt may be committed after its browser-tested commit."""
    root = _machine_ready_root(tmp_path)
    automated_path = root / "data/derived/dashboard_review/automated_review_packet.json"
    automated = json.loads(automated_path.read_text(encoding="utf-8"))
    owner = build_packet(root)
    owner_path = root / "data/derived/dashboard_review/owner_review_packet.json"
    owner_path.write_text(json.dumps(owner), encoding="utf-8")
    tested_commit = "b" * 40
    receipt_commit = "c" * 40
    reviewed_automated = dict(automated)
    reviewed_automated["tested_commit"] = tested_commit
    reviewed_automated["screenshot_count"] = 44
    reviewed_owner = dict(owner)
    reviewed_owner["tested_commit"] = tested_commit
    reviewed_owner["current_head"] = tested_commit
    reviewed_automated_bytes = json.dumps(reviewed_automated).encode()
    reviewed_owner_bytes = json.dumps(reviewed_owner).encode()
    human = {
        "status": "approved_within_scope",
        "reviewed_at": "2026-08-20T00:00:00Z",
        "reviewer": "repository-owner",
        "commit": tested_commit,
        "automated_packet_sha256": hashlib.sha256(reviewed_automated_bytes).hexdigest(),
        "owner_packet_sha256": hashlib.sha256(reviewed_owner_bytes).hexdigest(),
        "scope": {"routes": list(ROUTES)},
    }
    _write_json(root, "data/derived/dashboard_review/human_review.json", human)
    historical = {
        (receipt_commit, "data/derived/dashboard_review/automated_review_packet.json"): (
            reviewed_automated_bytes
        ),
        (receipt_commit, "data/derived/dashboard_review/owner_review_packet.json"): (
            reviewed_owner_bytes
        ),
        (receipt_commit, "data/derived/dashboard_review/human_review.json"): json.dumps(
            human
        ).encode(),
    }

    monkeypatch.setattr(
        "reimburse_atlas.dashboard_review._git_file_at_commit",
        lambda _repo, commit, path: historical.get((commit, path.as_posix())),
    )
    monkeypatch.setattr(
        "reimburse_atlas.dashboard_review._commits_touching",
        lambda _repo, _path: (receipt_commit,),
    )

    evidence = dashboard_review_evidence(root)

    assert evidence["approval_mode"] == "standing_scoped"
    assert evidence["checks"]["human_scoped_approval"] is True


@pytest.mark.parametrize("delegated", [False, True])
def test_dashboard_standing_approval_fails_after_ui_fingerprint_change(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    delegated: bool,
) -> None:
    """A material dashboard change still requires accountable review."""
    root = _machine_ready_root(tmp_path)
    automated_path = root / "data/derived/dashboard_review/automated_review_packet.json"
    automated = json.loads(automated_path.read_text(encoding="utf-8"))
    owner = build_packet(root)
    owner_path = root / "data/derived/dashboard_review/owner_review_packet.json"
    owner_path.write_text(json.dumps(owner), encoding="utf-8")
    reviewed_commit = "b" * 40
    reviewed_automated = dict(automated)
    reviewed_automated["tested_commit"] = reviewed_commit
    reviewed_automated["source_fingerprint"] = "2" * 64
    reviewed_automated["screenshot_count"] = 44
    reviewed_owner = dict(owner)
    reviewed_owner["tested_commit"] = reviewed_commit
    reviewed_owner["source_fingerprint"] = "2" * 64
    historical = {
        "data/derived/dashboard_review/automated_review_packet.json": json.dumps(
            reviewed_automated
        ).encode(),
        "data/derived/dashboard_review/owner_review_packet.json": json.dumps(
            reviewed_owner
        ).encode(),
    }
    _write_json(
        root,
        "data/derived/dashboard_review/human_review.json",
        {
            "status": "approved_within_scope",
            "reviewed_at": "2026-08-20T00:00:00Z",
            "reviewer": "repository-owner",
            "commit": reviewed_commit,
            "automated_packet_sha256": hashlib.sha256(
                historical["data/derived/dashboard_review/automated_review_packet.json"]
            ).hexdigest(),
            "owner_packet_sha256": hashlib.sha256(
                historical["data/derived/dashboard_review/owner_review_packet.json"]
            ).hexdigest(),
        },
    )

    def historical_file(_repo: Path, commit: str, path: Path) -> bytes | None:
        if commit != reviewed_commit:
            return None
        return historical.get(path.as_posix())

    monkeypatch.setattr("reimburse_atlas.dashboard_review._git_file_at_commit", historical_file)

    evidence = dashboard_review_evidence(root)

    assert evidence["approval_mode"] == "invalid"
    assert evidence["checks"]["human_scoped_approval"] is False
    if delegated:
        human_path = root / "data/derived/dashboard_review/human_review.json"
        human = json.loads(human_path.read_text())
        human["scope"] = {"routes": list(ROUTES)}
        human_path.write_text(json.dumps(human))
        _write_json(
            root,
            "data/licence_review/standing_scope.json",
            {
                "schema_version": "standing-approval-v1",
                "dashboard": {
                    "renew_with_passing_automation": True,
                    "automated_packet_sha256": human["automated_packet_sha256"],
                    "owner_packet_sha256": human["owner_packet_sha256"],
                },
            },
        )
        evidence = dashboard_review_evidence(root)
        assert evidence["approval_mode"] == "standing_scoped"
        assert evidence["checks"]["human_scoped_approval"] is True
        automated["status"] = "fail"
        automated_path.write_text(json.dumps(automated))
        assert dashboard_review_evidence(root)["checks"]["automated_pass"] is False


@pytest.mark.parametrize("content", [None, b"not-json", b"[]"])
def test_historical_packet_reader_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    content: bytes | None,
) -> None:
    monkeypatch.setattr(
        "reimburse_atlas.dashboard_review._git_file_at_commit",
        lambda _repo, _commit, _path: content,
    )

    assert _json_at_commit(tmp_path, "a" * 40, Path("packet.json")) == {}


@pytest.mark.parametrize(
    ("human", "historical"),
    [
        ({}, {}),
        ({"commit": "a" * 40}, {}),
        (
            {"commit": "a" * 40, "automated_packet_sha256": "0" * 64},
            {"automated_review_packet.json": b"{}", "owner_review_packet.json": b"{}"},
        ),
        (
            {
                "commit": "a" * 40,
                "automated_packet_sha256": hashlib.sha256(b"{}").hexdigest(),
                "owner_packet_sha256": "0" * 64,
            },
            {"automated_review_packet.json": b"{}", "owner_review_packet.json": b"{}"},
        ),
    ],
)
def test_standing_approval_rejects_incomplete_historical_binding(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    human: dict[str, str],
    historical: dict[str, bytes],
) -> None:
    monkeypatch.setattr(
        "reimburse_atlas.dashboard_review._git_file_at_commit",
        lambda _repo, _commit, path: historical.get(path.name),
    )

    assert not _standing_approval_valid(
        tmp_path,
        automated={},
        owner={},
        human=human,
        source_fingerprint="1" * 64,
    )


def test_dashboard_data_fingerprint_covers_rendered_csv_files(tmp_path: Path) -> None:
    public = tmp_path / "apps/dashboard/public/data"
    public.mkdir(parents=True)
    dataset = public / "source_status.csv"
    dataset.write_text("source,status\nMBS,ready\n", encoding="utf-8")
    original = dashboard_data_fingerprint(tmp_path)

    dataset.write_text("source,status\nMBS,blocked\n", encoding="utf-8")

    assert dashboard_data_fingerprint(tmp_path) != original


def test_dashboard_data_fingerprint_normalizes_only_legacy_osf_research_label(
    tmp_path: Path,
) -> None:
    public = tmp_path / "apps/dashboard/public/data"
    public.mkdir(parents=True)
    project = public / "github_project_items.csv"
    legacy = (
        'id,labels,status\nquestion,"[""type:research"", ""type:osf"", '
        '""phase:analysis"", ""status:drafted""]",todo\n'
    )
    project.write_text(legacy, encoding="utf-8")
    reviewed = dashboard_data_fingerprint(tmp_path)

    project.write_text(legacy.replace('""type:osf"", ', ""), encoding="utf-8")

    assert dashboard_data_fingerprint(tmp_path) == reviewed

    project.write_text(legacy.replace(",todo", ",done"), encoding="utf-8")

    assert dashboard_data_fingerprint(tmp_path) != reviewed


def test_dashboard_data_fingerprint_ignores_workflow_use_line_movement_at_baseline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    public = tmp_path / "apps/dashboard/public/data"
    public.mkdir(parents=True)
    receipt = public / "workflow_uses.csv"
    baseline = (
        "action,line,ref,uses,workflow\n"
        "actions/checkout,10,aaaaaaaa,actions/checkout@aaaaaaaa,.github/workflows/ci.yml\n"
    )
    receipt.write_text(baseline, encoding="utf-8")
    monkeypatch.setattr(
        "reimburse_atlas.dashboard_review._git_file_at_commit",
        lambda _repo, _commit, path: (
            baseline.encode("utf-8") if path == receipt.relative_to(tmp_path) else None
        ),
    )
    original = dashboard_data_fingerprint(tmp_path, self_attestation_commit="a" * 40)

    receipt.write_text(baseline.replace(",10,", ",20,"), encoding="utf-8")

    assert dashboard_data_fingerprint(tmp_path, self_attestation_commit="a" * 40) == original

    receipt.write_text(baseline.replace("aaaaaaaa", "bbbbbbbb"), encoding="utf-8")

    assert dashboard_data_fingerprint(tmp_path, self_attestation_commit="a" * 40) != original


def test_dashboard_data_fingerprint_preserves_duplicate_workflow_use_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    public = tmp_path / "apps/dashboard/public/data"
    public.mkdir(parents=True)
    receipt = public / "workflow_uses.csv"
    baseline = (
        "action,line,ref,uses,workflow\n"
        "actions/upload-artifact,10,aaaaaaaa,actions/upload-artifact@aaaaaaaa,.github/workflows/ci.yml\n"
        "actions/upload-artifact,20,aaaaaaaa,actions/upload-artifact@aaaaaaaa,.github/workflows/ci.yml\n"
    )
    receipt.write_text(baseline, encoding="utf-8")

    def baseline_file(_repo: Path, _commit: str, path: Path) -> bytes | None:
        return baseline.encode("utf-8") if path == receipt.relative_to(tmp_path) else None

    monkeypatch.setattr("reimburse_atlas.dashboard_review._git_file_at_commit", baseline_file)
    original = dashboard_data_fingerprint(tmp_path, self_attestation_commit="a" * 40)
    receipt.write_text(baseline.replace(",10,", ",30,").replace(",20,", ",40,"), encoding="utf-8")

    assert dashboard_data_fingerprint(tmp_path, self_attestation_commit="a" * 40) == original


def test_dashboard_data_fingerprint_ignores_only_its_release_gate_receipt(
    tmp_path: Path,
) -> None:
    public = tmp_path / "apps/dashboard/public/data"
    public.mkdir(parents=True)
    gates = public / "release_gates.csv"
    gates.write_text(
        "category,evidence,id,recommended_action,required,status\n"
        "dashboard,head=aaa failed_checks=human_scoped_approval,"
        "dashboard_human_review,Review,False,blocked\n"
        "release,registration=pending,osf_registration,Wait,False,blocked\n",
        encoding="utf-8",
    )
    original = dashboard_data_fingerprint(tmp_path)
    gates.write_text(
        "category,evidence,id,recommended_action,required,status\n"
        "dashboard,head=bbb failed_checks=none,"
        "dashboard_human_review,Review,False,pass\n"
        "release,registration=pending,osf_registration,Wait,False,blocked\n",
        encoding="utf-8",
    )

    assert dashboard_data_fingerprint(tmp_path) == original


def test_dashboard_data_fingerprint_ignores_operational_gate_receipts(tmp_path: Path) -> None:
    public = tmp_path / "apps/dashboard/public"
    data = public / "data"
    data.mkdir(parents=True)
    (data / "final_handoff_tasks.csv").write_text("id,status\na,blocked\n", encoding="utf-8")
    (data / "release_gates.csv").write_text("id,status\na,blocked\n", encoding="utf-8")
    (public / "status.json").write_text('{"release_ready":false}\n', encoding="utf-8")
    original = dashboard_data_fingerprint(tmp_path)

    (data / "final_handoff_tasks.csv").write_text("id,status\na,complete\n", encoding="utf-8")
    (data / "release_gates.csv").write_text("id,status\na,pass\n", encoding="utf-8")
    (public / "status.json").write_text('{"release_ready":true}\n', encoding="utf-8")

    assert dashboard_data_fingerprint(tmp_path) == original


def test_dashboard_data_fingerprint_ignores_derived_source_drift_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    public = tmp_path / "apps/dashboard/public/data"
    public.mkdir(parents=True)
    receipt = public / "source_drift_report.csv"
    baseline = (
        "id,left_checksum_sha256,status\n"
        "source_drift_github_project_jsonl_to_github_project_csv,aaa,pass\n"
        "source_drift_final_handoff_jsonl_to_final_handoff_csv,bbb,pass\n"
        "source_drift_data_quality_jsonl_to_data_quality_csv,ccc,pass\n"
    )
    receipt.write_text(baseline, encoding="utf-8")

    underlying = public / "source_content_validation.csv"
    underlying.write_text("id,status\nsource,pass\n", encoding="utf-8")

    def baseline_file(_repo: Path, _commit: str, path: Path) -> bytes | None:
        return baseline.encode("utf-8") if path == receipt.relative_to(tmp_path) else None

    monkeypatch.setattr("reimburse_atlas.dashboard_review._git_file_at_commit", baseline_file)
    original = dashboard_data_fingerprint(tmp_path, self_attestation_commit="a" * 40)
    receipt.write_text(
        baseline
        .replace(",aaa,", ",new-project-checksum,")
        .replace(",bbb,", ",new-handoff-checksum,")
        .replace(",ccc,", ",changed-data-quality-checksum,"),
        encoding="utf-8",
    )

    assert dashboard_data_fingerprint(tmp_path, self_attestation_commit="a" * 40) == original

    underlying.write_text("id,status\nsource,blocked\n", encoding="utf-8")

    assert dashboard_data_fingerprint(tmp_path, self_attestation_commit="a" * 40) != original


def test_public_status_normalization_replaces_only_dashboard_receipt() -> None:
    baseline = {
        "blockers": [
            {"id": "dashboard_human_review", "status": "blocked", "summary": "review pending"},
            {"id": "osf_registration", "status": "blocked", "summary": "snapshot missing"},
        ]
    }
    current = {
        "blockers": [
            {"id": "dashboard_human_review", "status": "pass", "summary": "approved"},
            {"id": "osf_registration", "status": "pass", "summary": "registration public"},
        ]
    }

    normalized = json.loads(
        normalize_public_status_dashboard_receipt(
            json.dumps(current).encode(),
            json.dumps(baseline).encode(),
        )
    )

    assert normalized["blockers"][0] == baseline["blockers"][0]
    assert normalized["blockers"][1] == current["blockers"][1]


def test_public_status_normalization_removes_dashboard_readiness_cycle() -> None:
    baseline = {
        "blockers": [{"id": "dashboard_human_review"}],
        "evidence": {
            "evidence_ready_rows": 5,
            "evidence_release_ready": False,
            "research_publication_ready": False,
            "status": "not_ready",
        },
        "publication": {"status": "gated"},
    }
    current = {
        "blockers": [],
        "evidence": {
            "evidence_ready_rows": 5,
            "evidence_release_ready": True,
            "research_publication_ready": True,
            "status": "ready",
        },
        "publication": {"status": "ready"},
    }

    normalized = json.loads(
        normalize_public_status_dashboard_receipt(
            json.dumps(current).encode(),
            json.dumps(baseline).encode(),
        )
    )

    assert normalized["evidence"]["evidence_ready_rows"] == 5
    assert normalized["evidence"]["evidence_release_ready"] is False
    assert normalized["evidence"]["research_publication_ready"] is False
    assert normalized["evidence"]["status"] == "not_ready"
    assert normalized["publication"]["status"] == "gated"


def test_csv_normalization_replaces_only_named_self_receipt() -> None:
    baseline = b"id,status\nfinal_dashboard_visual_review,blocked\nosf_registration,blocked\n"
    current = b"id,status\nfinal_dashboard_visual_review,complete\nosf_registration,pass\n"

    normalized = normalize_csv_receipt(
        current,
        baseline,
        key="id",
        value="final_dashboard_visual_review",
    )

    assert normalized == (
        b"id,status\nfinal_dashboard_visual_review,blocked\nosf_registration,pass\n"
    )


def test_receipt_normalization_fails_closed_for_malformed_inputs() -> None:
    malformed = b"{invalid"
    assert normalize_public_status_dashboard_receipt(malformed, b"{}") == malformed
    non_object = b"[]"
    assert normalize_public_status_dashboard_receipt(non_object, b"{}") == non_object
    missing_blockers = b'{"evidence": {}}'
    assert (
        normalize_public_status_dashboard_receipt(missing_blockers, b'{"blockers": []}')
        == missing_blockers
    )
    baseline_with_noise = b'{"blockers": [null, {"id": "dashboard_human_review"}]}'
    normalized = normalize_public_status_dashboard_receipt(
        b'{"blockers": [null]}',
        baseline_with_noise,
    )
    assert json.loads(normalized)["blockers"] == [
        None,
        {"id": "dashboard_human_review"},
    ]

    mismatched = b"id,status\nreview,pass\n"
    assert (
        normalize_csv_receipt(
            mismatched,
            b"name,status\nreview,blocked\n",
            key="id",
            value="review",
        )
        == mismatched
    )
    assert (
        normalize_csv_receipt(
            mismatched,
            b"id,status\nother,blocked\n",
            key="id",
            value="review",
        )
        == mismatched
    )


def test_owner_packet_does_not_hash_its_dependent_release_summary() -> None:
    """Prevent a cryptographic cycle between review evidence and release readiness."""
    assert Path("data/derived/release_readiness/summary.json") not in PROVENANCE_INPUTS


def test_resolve_repo_head_reads_detached_and_loose_refs(tmp_path: Path) -> None:
    git = tmp_path / ".git"
    git.mkdir()
    (git / "HEAD").write_text("a" * 40, encoding="utf-8")
    assert resolve_repo_head(tmp_path) == "a" * 40

    (git / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
    branch = git / "refs/heads/main"
    branch.parent.mkdir(parents=True)
    branch.write_text("b" * 40, encoding="utf-8")
    assert resolve_repo_head(tmp_path) == "b" * 40


def test_resolve_repo_head_reads_worktree_packed_ref(tmp_path: Path) -> None:
    common = tmp_path / "common"
    worktree_git = common / "worktrees/current"
    worktree_git.mkdir(parents=True)
    (worktree_git / "HEAD").write_text("ref: refs/heads/release", encoding="utf-8")
    (worktree_git / "commondir").write_text("../..", encoding="utf-8")
    (common / "packed-refs").write_text(
        f"# pack-refs\n{'c' * 40} refs/heads/release\n^{'d' * 40}\n",
        encoding="utf-8",
    )
    (tmp_path / ".git").write_text(
        f"gitdir: {worktree_git.as_posix()}",
        encoding="utf-8",
    )

    assert resolve_repo_head(tmp_path) == "c" * 40


def test_resolve_repo_head_rejects_invalid_gitdir_marker(tmp_path: Path) -> None:
    (tmp_path / ".git").write_text("invalid", encoding="utf-8")

    assert resolve_repo_head(tmp_path) is None

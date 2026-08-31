"""Synthetic receipt-contract checks; no remote access or raw payload verification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError

from reimburse_atlas.pbs_publication_receipt import (
    Evidence,
    PublicationReceipt,
    evidence_errors,
    load_receipt,
)
from scripts.check_pbs_publication_receipt import main

ROOT = Path(__file__).resolve().parents[2]
DRAFT = ROOT / ("conductor/archive/track_pbs_raw_archive_20260831/publication-receipt.pending.json")


@pytest.fixture
def complete() -> dict[str, Any]:
    """Create synthetic complete attestations, never mutate the real pending draft."""
    row = json.loads(DRAFT.read_text())
    row["fresh_readback"] = {
        **row["remote_inventory"],
        "report": {"path": "data/local/fresh-readback.json", "sha256": "a" * 64},
        "download_report": {"path": "data/local/fresh-download.json", "sha256": "b" * 64},
        "origin": "independent_fresh_fixed_revision_download",
        "all_payload_hashes_verified": True,
        "exact_inventory_verified": True,
        "canonical_bound_readback_verified": True,
        "permission_and_readme_verified": True,
    }

    def portable(value: Any) -> None:
        if isinstance(value, dict):
            mapping = cast("dict[str, Any]", value)
            if set(mapping) == {"path", "sha256"}:
                mapping["path"] = str(mapping["path"]).replace(
                    "data/local/", "data/derived/pbs-proof-test/", 1
                )
            else:
                for child in mapping.values():
                    portable(child)
        elif isinstance(value, list):
            for child in cast("list[Any]", value):
                portable(child)

    portable(row)
    return row


def test_pending_draft_never_claims_publication_or_closeout() -> None:
    receipt = load_receipt(DRAFT)
    assert receipt.publication_state == "not_asserted"
    assert receipt.publication_blockers() == ["fresh_readback_missing"]
    assert receipt.closeout_delivery is None
    assert receipt.metadata_reconciliation is not None
    assert receipt.metadata_reconciliation.added_exact_lfs_rules == 963
    assert receipt.metadata_reconciliation.nonraw_byte_identical == 23


def test_complete_evidence_does_not_auto_promote(complete: dict[str, Any]) -> None:
    receipt = PublicationReceipt.model_validate(complete)
    assert not receipt.publication_blockers()
    assert receipt.publication_state == "not_asserted"


def test_available_viewer_cannot_replace_fresh_download() -> None:
    row = json.loads(DRAFT.read_text())
    row.update(publication_state="published_verified", viewer_status="available")
    with pytest.raises(ValidationError):
        PublicationReceipt.model_validate(row)


def test_local_cache_is_not_an_independent_download(complete: dict[str, Any]) -> None:
    complete["fresh_readback"]["origin"] = "local_stage"
    with pytest.raises(ValidationError):
        PublicationReceipt.model_validate(complete)


@pytest.mark.parametrize("viewer", ["external_pending", "available", "unavailable"])
def test_viewer_is_not_a_raw_verification_gate(complete: dict[str, Any], viewer: str) -> None:
    complete.update(publication_state="published_verified", viewer_status=viewer)
    assert PublicationReceipt.model_validate(complete).publication_state == "published_verified"


@pytest.mark.parametrize(
    "missing",
    ["source_delivery_evidence", "remote_inventory", "metadata_reconciliation", "fresh_readback"],
)
def test_every_publication_proof_is_required(complete: dict[str, Any], missing: str) -> None:
    complete.update(publication_state="published_verified")
    complete[missing] = None
    with pytest.raises(ValidationError):
        PublicationReceipt.model_validate(complete)


@pytest.mark.parametrize("proof", ["remote_inventory", "fresh_readback"])
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("revision", "c" * 40),
        ("manifest_sha256", "d" * 64),
        ("payload_count", 1706),
        ("payload_bytes", 9216771434),
        ("artifact_count", 1707),
        ("payload_count", True),
    ],
)
def test_batch_proofs_bind_revision_manifest_counts(
    complete: dict[str, Any], proof: str, field: str, value: object
) -> None:
    complete[proof][field] = value
    with pytest.raises(ValidationError):
        PublicationReceipt.model_validate(complete)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("revision", "c" * 40),
        ("exception_path", "README.md"),
        ("nonraw_byte_identical", 24),
        ("regular_payloads", 91),
        ("original_attribute_bytes_preserved", False),
        ("only_expected_raw_lfs_rules_added", False),
        ("nonraw_effective_attributes_preserved", False),
        ("regular_payloads_not_marked_lfs", False),
        ("eight_configs_and_root_card_unchanged", False),
    ],
)
def test_metadata_exception_is_bounded(complete: dict[str, Any], field: str, value: object) -> None:
    complete["metadata_reconciliation"][field] = value
    with pytest.raises(ValidationError):
        PublicationReceipt.model_validate(complete)


@pytest.mark.parametrize(
    "field",
    [
        "all_payload_hashes_verified",
        "exact_inventory_verified",
        "canonical_bound_readback_verified",
        "permission_and_readme_verified",
    ],
)
def test_partial_readback_cannot_be_proof(complete: dict[str, Any], field: str) -> None:
    complete["fresh_readback"][field] = False
    with pytest.raises(ValidationError):
        PublicationReceipt.model_validate(complete)


@pytest.mark.parametrize("change", ["canonical", "reports", "omissions", "history", "extra"])
def test_preserve_full_corpus_inputs(complete: dict[str, Any], change: str) -> None:
    if change == "canonical":
        complete["canonical_receipts"][1] = complete["canonical_receipts"][0]
    elif change == "reports":
        complete["full_corpus_reports"].pop()
    elif change == "omissions":
        complete["retained_omissions"] = []
    elif change == "history":
        complete["historical_completeness_asserted"] = True
    else:
        complete["owner_approval_required"] = True
    with pytest.raises(ValidationError):
        PublicationReceipt.model_validate(complete)


@pytest.mark.parametrize(
    "path", ["/outside/proof.json", "data/local/../proof", "data/raw_live/payload"]
)
def test_unsafe_evidence_paths_rejected(path: str) -> None:
    with pytest.raises(ValidationError):
        Evidence(path=path, sha256="a" * 64)


def test_duplicate_json_keys_rejected(tmp_path: Path) -> None:
    receipt = tmp_path / "receipt.json"
    receipt.write_text('{"nested":{"status":"fail","status":"pass"}}')
    with pytest.raises(ValueError, match="duplicate JSON key"):
        load_receipt(receipt)


def test_missing_changed_and_symlink_evidence_fail(tmp_path: Path) -> None:
    receipt = load_receipt(DRAFT)
    assert len(evidence_errors(receipt, tmp_path)) == len(receipt.evidence())
    reference = receipt.permission
    path = tmp_path / reference.path
    path.parent.mkdir(parents=True)
    path.write_text("changed")
    assert f"checksum_mismatch:{reference.path}" in evidence_errors(receipt, tmp_path)
    path.unlink()
    path.symlink_to(DRAFT)
    assert f"unreadable_evidence:{reference.path}" in evidence_errors(receipt, tmp_path)


def test_non_json_attestations_cannot_publish_even_with_matching_hashes(
    complete: dict[str, Any],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    complete["closeout_delivery"] = {
        "pr802_merge": "1" * 40,
        "pr804_merge": "2" * 40,
        "validated_commit": "3" * 40,
        "validation_report": {
            "path": "data/derived/pbs-proof-test/validation.json",
            "sha256": "4" * 64,
        },
    }

    def bind(value: Any) -> None:
        if isinstance(value, dict):
            mapping = cast("dict[str, Any]", value)
            if set(mapping) == {"path", "sha256"}:
                path = tmp_path / str(mapping["path"])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"synthetic parent attestation\n")
                mapping["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            else:
                for child in mapping.values():
                    bind(child)
        elif isinstance(value, list):
            for child in cast("list[Any]", value):
                bind(child)

    bind(complete)
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(complete))
    monkeypatch.setattr("sys.argv", ["check", str(path), "--evidence-root", str(tmp_path)])
    assert main() == 1
    result = json.loads(capsys.readouterr().out)
    assert any("unreadable_evidence" in error for error in result["closeout_blockers"])
    assert result["network_performed"] is False
    assert result["track_archived"] is False
    complete["publication_state"] = "published_verified"
    path.write_text(json.dumps(complete))
    before = path.read_bytes()
    assert main() == 1
    assert path.read_bytes() == before
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "blocked"
    assert result["publication_state"] == "not_asserted"


def write_proof(root: Path, reference: dict[str, Any], value: object) -> None:
    """Bind a synthetic native JSON proof to its exact test bytes."""
    path = root / reference["path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".jsonl":
        content = "".join(json.dumps(row) + "\n" for row in cast("list[object]", value))
    else:
        content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.write_text(content)
    reference["sha256"] = hashlib.sha256(content.encode()).hexdigest()


@pytest.fixture
def native_case(complete: dict[str, Any], tmp_path: Path) -> dict[str, Any]:
    """A two-payload native-shaped case, including the preserved metadata failure."""
    row = complete
    row.update(payload_count=2, payload_bytes=8)
    row.update(viewer_status="external_pending", viewer_observation=None, viewer_observed_at=None)
    for proof in (row["remote_inventory"], row["fresh_readback"]):
        proof.update(payload_count=2, payload_bytes=8, artifact_count=4)
    meta = row["metadata_reconciliation"]
    meta.update(lfs_payloads=1, regular_payloads=1, added_exact_lfs_rules=1)
    write_proof(tmp_path, row["permission"], {"schema_version": "pbs-raw-permission-v2"})
    selected = [
        {
            "id": identity,
            "source_id": "au_pbs",
            "source_version_id": f"pbs_{identity}_202608",
            "citation_key": f"pbs_{identity}_citation",
            "source_url": f"https://www.pbs.gov.au/publication/schedule/2026/08/{identity}{suffix}",
            "file_name": f"{identity}{suffix}",
            "status": "downloaded",
            "cache_path": f"data/raw_live/historical_sources/{identity}{suffix}",
            "byte_size": 4,
            "checksum_sha256": "a" * 64,
        }
        for identity, suffix in (("first", ".pdf"), ("second", ".zip"))
    ]
    for ref, rows in zip(
        row["canonical_receipts"], [selected, [{"id": "missing"}], []], strict=True
    ):
        write_proof(tmp_path, ref, rows)
    write_proof(tmp_path, row["selection"], selected)
    for ref in row["full_corpus_reports"]:
        write_proof(
            tmp_path,
            ref,
            {
                "schema_version": "pbs-raw-archive-staging-v1",
                "mode": "dry_run",
                "status": "blocked",
                "publication_state": "not_asserted",
                "errors": [{"id": "missing", "error": "not_acquired"}],
                "coverage": {"requested_receipts": 3},
            },
        )
    write_proof(
        tmp_path,
        row["source_delivery_evidence"],
        {
            "state": "MERGED",
            "mergeCommit": {"oid": row["source_merge"]},
            "mergedAt": "2026-08-31T10:00:00Z",
            "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
        },
    )
    inventory = {
        "schema_version": "pbs-remote-metadata-verification-v1",
        "verification_kind": "remote_metadata_only",
        "repo_id": row["repo_id"],
        "revision": row["upload_revision"],
        "expected_raw_count": 4,
        "missing_raw": [],
        "raw_content_metadata_mismatch": [],
        "unexpected_files": [],
        "missing_nonraw": [],
        "status": "fail",
        "changed_nonraw": [".gitattributes"],
        "failure_codes": ["changed_nonraw", "card_metadata_mismatch"],
    }
    write_proof(tmp_path, row["remote_inventory"]["report"], inventory)
    meta["original_strict_failure"] = dict(row["remote_inventory"]["report"])
    checks = (
        "added_paths_exactly_equal_uncovered_expected_lfs_files",
        "all_1_lfs_objects_have_correct_effective_attributes",
        "all_8_explicit_config_paths_present_and_unchanged",
        "all_1_regular_objects_not_marked_lfs",
        "all_added_lines_exact_lfs_filter_diff_merge_text_rule",
        "all_added_paths_manifest_allowlisted",
        "all_added_paths_remote_lfs_objects",
        "exactly_23_nonraw_files_identical_by_blob_size_lfs_metadata",
        "manifest_and_archive_readme_attributes_unchanged",
        "nonraw_effective_attributes_unchanged",
        "only_gitattributes_nonraw_bytes_changed",
        "original_attribute_bytes_preserved_as_exact_prefix",
        "parsed_card_data_unchanged",
        "regular_object_attributes_unchanged",
        "root_readme_exact_bytes_unchanged",
    )
    write_proof(
        tmp_path,
        meta["report"],
        {
            "schema_version": "pbs-additive-lfs-reconciliation-v1",
            "status": meta["status"],
            "repo_id": row["repo_id"],
            "archive_revision": row["upload_revision"],
            "baseline_revision": meta["baseline_revision"],
            "baseline_nonraw_count": 24,
            "nonraw_byte_identical_count": 23,
            "exact_24_of_24_nonraw_parity_claimed": False,
            "original_strict_receipt_preserved": True,
            "original_strict_receipt_sha256": meta["original_strict_failure"]["sha256"],
            "original_strict_verification_status": "fail",
            "original_strict_failure_codes": ["changed_nonraw", "card_metadata_mismatch"],
            "raw_inventory_status": "pass_at_archive_revision_in_original_receipt",
            "checks": dict.fromkeys(checks, True),
            "technical_exception": {
                "file": ".gitattributes",
                "added_exact_raw_lfs_rules": 1,
                "removed_or_changed_original_bytes": 0,
                "added_paths": [f"raw/pbs/payloads/first/{'a' * 64}.pdf"],
            },
            "card": {"parsed_card_exact": True, "root_readme_exact": True},
        },
    )
    readback = {
        "schema_version": "pbs-raw-archive-staging-v2",
        "status": "verified",
        "mode": "readback",
        "archive_prefix": "raw/pbs",
        "errors": [],
        "publication_state": "not_asserted",
        "network_publication_performed": False,
        "archive_readme_checksum_sha256": row["readme_sha256"],
        "permission_record": row["permission"]["path"],
        "permission_record_checksum_sha256": row["permission"]["sha256"],
        "coverage": {
            "requested_receipts": 2,
            "verified_files": 2,
            "failed_receipts": 0,
            "failed_operations": 0,
            "complete_for_requested_batch": True,
            "historical_completeness_asserted": False,
        },
        "files": [
            {
                "id": item["id"],
                "source_id": item["source_id"],
                "source_version_id": item["source_version_id"],
                "citation_key": item["citation_key"],
                "source_url": item["source_url"],
                "original_source_filename": item["file_name"],
                "acquisition_status": item["status"],
                "archive_path": (
                    f"raw/pbs/payloads/{item['id']}/{item['checksum_sha256']}"
                    f"{Path(item['file_name']).suffix}"
                ),
                "byte_size": item["byte_size"],
                "checksum_sha256": item["checksum_sha256"],
            }
            for item in selected
        ],
    }
    stage = (json.dumps({**readback, "mode": "stage"}, indent=2, sort_keys=True) + "\n").encode()
    bind_full_corpus_files(tmp_path, row, readback["files"])
    row["manifest_sha256"] = hashlib.sha256(stage).hexdigest()
    for proof in (row["remote_inventory"], row["fresh_readback"]):
        proof["manifest_sha256"] = row["manifest_sha256"]
    write_proof(tmp_path, row["fresh_readback"]["report"], readback)
    write_proof(
        tmp_path,
        row["fresh_readback"]["download_report"],
        {
            "schema_version": "pbs-fresh-download-v1",
            "status": "verified",
            "origin": "independent_fresh_fixed_revision_download",
            "repo_id": row["repo_id"],
            "revision": row["upload_revision"],
            "download_exit_code": 0,
            "force_download": True,
            "xet_disabled": True,
            "include_prefix": "raw/pbs/",
            "metadata_count": 4,
            "all_metadata_revisions_match": True,
            "exact_metadata_inventory": True,
            "payload_count": 2,
            "payload_bytes": 8,
            "artifact_count": 4,
            "manifest_sha256": row["manifest_sha256"],
            "metadata_inventory_sha256": "a" * 64,
            "canonical_readback_performed_by_this_script": False,
        },
    )
    row["closeout_delivery"] = {
        "pr802_merge": "1" * 40,
        "pr804_merge": "2" * 40,
        "validated_commit": "3" * 40,
        "validation_report": {
            "path": "data/derived/pbs-proof-test/validation.json",
            "sha256": "4" * 64,
        },
    }
    write_proof(
        tmp_path,
        cast("dict[str, Any]", row["closeout_delivery"]["validation_report"]),
        {
            "schema_version": "pbs-closeout-validation-v1",
            "status": "pass",
            "validated_commit": "3" * 40,
            "pr802_merge": "1" * 40,
            "pr804_merge": "2" * 40,
            "regeneration_fixed_point_verified": True,
            "local_quality": {
                "schema_version": "local-quality-gates-v1",
                "profile": "ci",
                "gate_count": 27,
                "passed": 27,
                "failed": 0,
                "blocked_network": 0,
                "missing_tool": 0,
                "timed_out": 0,
                "wrong_tool": 0,
                "skipped": 0,
                "blocking_failures": 0,
            },
        },
    )
    return row


def test_native_proofs_pass_without_viewer_gate(
    native_case: dict[str, Any], tmp_path: Path
) -> None:
    native_case["publication_state"] = "published_verified"
    receipt = PublicationReceipt.model_validate(native_case)
    assert receipt.viewer_status == "external_pending"
    assert evidence_errors(receipt, tmp_path) == []


@pytest.mark.parametrize("require_integration", [False, True])
def test_cli_publication_without_integration_validation(
    native_case: dict[str, Any],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    require_integration: bool,
) -> None:
    native_case.update(publication_state="published_verified", closeout_delivery=None)
    assert evidence_errors(PublicationReceipt.model_validate(native_case), tmp_path) == []
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(native_case))
    before = path.read_bytes()
    argv = ["check", str(path), "--evidence-root", str(tmp_path)]
    if require_integration:
        argv.append("--require-integration")
    monkeypatch.setattr("sys.argv", argv)

    assert main() == int(require_integration)
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == ("blocked" if require_integration else "publication_verified")
    assert result["publication_state"] == "published_verified"
    assert result["publication_blockers"] == []
    assert result["closeout_blockers"] == ["final_integration_validation_missing"]
    assert result["network_performed"] is False
    assert result["track_archived"] is False
    assert path.read_bytes() == before


@pytest.mark.parametrize("require_integration", [False, True])
def test_cli_malformed_proof_without_integration_fails_closed(
    native_case: dict[str, Any],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    require_integration: bool,
) -> None:
    native_case.update(publication_state="published_verified", closeout_delivery=None)
    write_proof(tmp_path, native_case["fresh_readback"]["report"], {})
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(native_case))
    before = path.read_bytes()
    argv = ["check", str(path), "--evidence-root", str(tmp_path)]
    if require_integration:
        argv.append("--require-integration")
    monkeypatch.setattr("sys.argv", argv)

    assert main() == 1
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "blocked"
    assert result["publication_state"] == "not_asserted"
    assert "invalid_canonical_readback_proof" in result["publication_blockers"]
    assert "final_integration_validation_missing" in result["closeout_blockers"]
    assert result["network_performed"] is False
    assert result["track_archived"] is False
    assert path.read_bytes() == before


@pytest.mark.parametrize("proof", ["readback", "download", "validation"])
def test_failed_inventory_reuse_regression(
    native_case: dict[str, Any],
    tmp_path: Path,
    proof: str,
) -> None:
    failed = native_case["remote_inventory"]["report"]
    native_case["publication_state"] = "published_verified"
    if proof == "validation":
        native_case["closeout_delivery"]["validation_report"] = failed
    else:
        key = "report" if proof == "readback" else "download_report"
        native_case["fresh_readback"][key] = failed
    assert evidence_errors(PublicationReceipt.model_validate(native_case), tmp_path)


@pytest.mark.parametrize(
    ("proof", "field", "value"),
    [
        ("readback", "status", "blocked"),
        ("readback", "mode", "stage"),
        ("readback", "errors", [{"error": "staging_failed"}]),
        ("readback", "archive_readme_checksum_sha256", "0" * 64),
        ("readback", "permission_record_checksum_sha256", "0" * 64),
        ("download", "status", "failed"),
        ("download", "revision", "0" * 40),
        ("download", "origin", "local_stage"),
        ("download", "download_exit_code", 1),
        ("download", "download_exit_code", False),
        ("download", "metadata_count", 3),
        ("download", "payload_bytes", 7),
        ("download", "exact_metadata_inventory", False),
        ("download", "manifest_sha256", "0" * 64),
        ("validation", "status", "failed"),
        ("validation", "validated_commit", "0" * 40),
        ("source", "state", "OPEN"),
        ("source", "mergeCommit", {"oid": "0" * 40}),
        ("metadata", "status", "failed"),
        ("metadata", "original_strict_receipt_preserved", False),
    ],
)
def test_native_fields_checked_even_after_rehashing(
    native_case: dict[str, Any],
    tmp_path: Path,
    proof: str,
    field: str,
    value: object,
) -> None:
    refs = {
        "readback": native_case["fresh_readback"]["report"],
        "download": native_case["fresh_readback"]["download_report"],
        "validation": native_case["closeout_delivery"]["validation_report"],
        "source": native_case["source_delivery_evidence"],
        "metadata": native_case["metadata_reconciliation"]["report"],
    }
    ref = refs[proof]
    document = json.loads((tmp_path / ref["path"]).read_text())
    document[field] = value
    write_proof(tmp_path, ref, document)
    assert evidence_errors(PublicationReceipt.model_validate(native_case), tmp_path)


def test_forged_readme_outer_claim_fails(native_case: dict[str, Any], tmp_path: Path) -> None:
    native_case["readme_sha256"] = "0" * 64
    assert "invalid_canonical_readback_proof" in evidence_errors(
        PublicationReceipt.model_validate(native_case), tmp_path
    )


def test_published_receipt_cannot_depend_on_ignored_local_evidence(
    complete: dict[str, Any],
) -> None:
    complete["publication_state"] = "published_verified"
    complete["fresh_readback"]["download_report"]["path"] = "data/local/download.json"
    with pytest.raises(ValidationError):
        PublicationReceipt.model_validate(complete)


def test_changed_reconstructed_manifest_cannot_reuse_outer_binding(
    native_case: dict[str, Any],
    tmp_path: Path,
) -> None:
    ref = native_case["fresh_readback"]["report"]
    report = json.loads((tmp_path / ref["path"]).read_text())
    report["extra_unbound_provenance"] = "invented"
    write_proof(tmp_path, ref, report)
    assert "invalid_canonical_readback_proof" in evidence_errors(
        PublicationReceipt.model_validate(native_case), tmp_path
    )


def test_original_p1_cli_reproduction_fails(
    native_case: dict[str, Any],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    failed = native_case["remote_inventory"]["report"]
    native_case["fresh_readback"].update(report=failed, download_report=failed)
    native_case["closeout_delivery"]["validation_report"] = failed
    native_case.update(publication_state="published_verified", readme_sha256="0" * 64)
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(native_case))
    monkeypatch.setattr("sys.argv", ["check", str(path), "--evidence-root", str(tmp_path)])
    assert main() == 1
    result = json.loads(capsys.readouterr().out)
    assert result["publication_state"] == "not_asserted"
    assert result["claimed_publication_state"] == "published_verified"
    assert set(result["publication_blockers"]) >= {
        "invalid_fresh_download_proof",
        "invalid_canonical_readback_proof",
        "invalid_closeout_validation_proof",
    }


@pytest.mark.parametrize("field", ["failed_receipts", "failed_operations", "verified_files"])
def test_readback_coverage_cannot_be_hidden_by_outer_success(
    native_case: dict[str, Any],
    tmp_path: Path,
    field: str,
) -> None:
    ref = native_case["fresh_readback"]["report"]
    document = json.loads((tmp_path / ref["path"]).read_text())
    document["coverage"][field] = 1
    write_proof(tmp_path, ref, document)
    assert "invalid_canonical_readback_proof" in evidence_errors(
        PublicationReceipt.model_validate(native_case), tmp_path
    )


def test_readback_rejects_another_legitimate_canonical_selection(
    native_case: dict[str, Any],
    tmp_path: Path,
) -> None:
    ref = native_case["selection"]
    rows = [json.loads(line) for line in (tmp_path / ref["path"]).read_text().splitlines()]
    replacement = json.loads(
        (tmp_path / native_case["canonical_receipts"][1]["path"]).read_text().strip()
    )
    rows[0] = replacement
    write_proof(tmp_path, ref, rows)
    assert evidence_errors(PublicationReceipt.model_validate(native_case), tmp_path) == [
        "invalid_canonical_readback_proof"
    ]


@pytest.mark.parametrize(("field", "value"), [("checksum_sha256", "0" * 64), ("byte_size", 5)])
def test_readback_fingerprint_must_match_selection_even_with_rebound_manifest(
    native_case: dict[str, Any],
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    ref = native_case["fresh_readback"]["report"]
    report = json.loads((tmp_path / ref["path"]).read_text())
    report["files"][0][field] = value
    rebind_readback(tmp_path, native_case, report)
    assert evidence_errors(PublicationReceipt.model_validate(native_case), tmp_path) == [
        "invalid_canonical_readback_proof"
    ]


def rebind_readback(root: Path, receipt: dict[str, Any], report: dict[str, Any]) -> None:
    """Rebind every downstream digest so only semantic provenance checks can fail."""
    total = sum(file["byte_size"] for file in report["files"])
    stage = (json.dumps({**report, "mode": "stage"}, indent=2, sort_keys=True) + "\n").encode()
    digest = hashlib.sha256(stage).hexdigest()
    receipt.update(manifest_sha256=digest, payload_bytes=total)
    for proof in (receipt["remote_inventory"], receipt["fresh_readback"]):
        proof.update(manifest_sha256=digest, payload_bytes=total)
    write_proof(root, receipt["fresh_readback"]["report"], report)
    download = receipt["fresh_readback"]["download_report"]
    document = json.loads((root / download["path"]).read_text())
    document.update(manifest_sha256=digest, payload_bytes=total)
    write_proof(root, download, document)


def bind_full_corpus_files(
    root: Path, receipt: dict[str, Any], files: list[dict[str, Any]]
) -> None:
    """Retain native verified rows alongside the full batch's preserved failures."""
    for ref in receipt["full_corpus_reports"]:
        document = json.loads((root / ref["path"]).read_text())
        document["files"] = files
        write_proof(root, ref, document)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("archive_path", f"raw/pbs/payloads/renamed/{'a' * 64}.pdf"),
        ("archive_path", f"raw/pbs/payloads/first/{'a' * 64}.zip"),
        ("archive_path", "../../outside.pdf"),
        ("original_source_filename", "different-schedule.pdf"),
        ("source_url", "https://www.pbs.gov.au/publication/schedule/2026/09/first.pdf"),
        ("source_version_id", "pbs_other_202609"),
        ("source_id", "other_source"),
        ("citation_key", "other_citation"),
        ("acquisition_status", "cached"),
    ],
)
@pytest.mark.parametrize("mutation", ["replace", "remove"])
def test_readback_provenance_must_match_selection_even_with_rebound_manifest(
    native_case: dict[str, Any],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    field: str,
    value: object,
    mutation: str,
) -> None:
    native_case.update(publication_state="published_verified", closeout_delivery=None)
    assert evidence_errors(PublicationReceipt.model_validate(native_case), tmp_path) == []
    ref = native_case["fresh_readback"]["report"]
    report = json.loads((tmp_path / ref["path"]).read_text())
    if mutation == "replace":
        report["files"][0][field] = value
    else:
        del report["files"][0][field]
    rebind_readback(tmp_path, native_case, report)
    assert evidence_errors(PublicationReceipt.model_validate(native_case), tmp_path) == [
        "invalid_canonical_readback_proof"
    ]
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(native_case))
    monkeypatch.setattr("sys.argv", ["check", str(path), "--evidence-root", str(tmp_path)])
    assert main() == 1
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "blocked"
    assert result["publication_state"] == "not_asserted"
    assert result["publication_blockers"] == ["invalid_canonical_readback_proof"]


@pytest.fixture
def native_variant_case(native_case: dict[str, Any], tmp_path: Path) -> dict[str, Any]:
    """An exact-replay variant inherits edition and citation from its selected parent."""
    selected = [
        json.loads(line)
        for line in (tmp_path / native_case["selection"]["path"]).read_text().splitlines()
    ]
    parent = selected[0]
    variant = {
        "id": "second",
        "source_id": parent["id"],
        "official_source_url": parent["source_url"] + "?variant=1",
        "archive_timestamp": "20260801000000",
        "archive_replay_url": (
            "https://web.archive.org/web/20260801000000id_/" + parent["source_url"]
        ),
        "archive_digest_verified": True,
        "status": "downloaded",
        "cache_path": "data/raw_live/historical_sources/second.pdf",
        "byte_size": 4,
        "checksum_sha256": "a" * 64,
    }
    write_proof(tmp_path, native_case["canonical_receipts"][0], [parent])
    write_proof(tmp_path, native_case["canonical_receipts"][2], [variant])
    write_proof(tmp_path, native_case["selection"], [parent, variant])
    ref = native_case["fresh_readback"]["report"]
    report = json.loads((tmp_path / ref["path"]).read_text())
    report["files"][1] = {
        **report["files"][0],
        "id": variant["id"],
        "source_url": variant["official_source_url"],
        "archive_path": f"raw/pbs/payloads/second/{'a' * 64}.pdf",
        "archive_timestamp": variant["archive_timestamp"],
        "archive_replay_url": variant["archive_replay_url"],
        "archive_original_url": parent["source_url"],
        "archive_identity_basis": "exact_replay_url",
    }
    rebind_readback(tmp_path, native_case, report)
    bind_full_corpus_files(tmp_path, native_case, report["files"])
    return native_case


def test_native_variant_provenance_passes(
    native_variant_case: dict[str, Any], tmp_path: Path
) -> None:
    assert evidence_errors(PublicationReceipt.model_validate(native_variant_case), tmp_path) == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("archive_timestamp", "20260802000000"),
        ("archive_replay_url", "https://web.archive.org/web/20260802000000id_/different.pdf"),
        ("archive_original_url", "https://www.pbs.gov.au/publication/schedule/2026/09/first.pdf"),
        ("archive_identity_basis", "exact_cdx_capture_and_payload_digests"),
        ("source_version_id", "pbs_variant_invented_edition"),
        ("citation_key", "pbs_variant_invented_citation"),
        ("original_source_filename", "second.pdf"),
    ],
)
@pytest.mark.parametrize("mutation", ["replace", "remove"])
def test_variant_provenance_cannot_be_rebound(
    native_variant_case: dict[str, Any],
    tmp_path: Path,
    field: str,
    value: object,
    mutation: str,
) -> None:
    assert evidence_errors(PublicationReceipt.model_validate(native_variant_case), tmp_path) == []
    ref = native_variant_case["fresh_readback"]["report"]
    report = json.loads((tmp_path / ref["path"]).read_text())
    if mutation == "replace":
        report["files"][1][field] = value
    else:
        del report["files"][1][field]
    rebind_readback(tmp_path, native_variant_case, report)
    assert evidence_errors(PublicationReceipt.model_validate(native_variant_case), tmp_path) == [
        "invalid_canonical_readback_proof"
    ]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("archive_path", f"raw/pbs/payloads/substituted/{'a' * 64}.pdf"),
        ("original_source_filename", "substituted.pdf"),
        ("source_url", "https://www.pbs.gov.au/publication/schedule/2026/09/first.pdf"),
        ("source_version_id", "pbs_other_edition"),
        ("citation_key", "other_citation"),
        ("acquisition_status", "cached"),
    ],
)
def test_rebinding_full_report_cannot_override_canonical_provenance(
    native_case: dict[str, Any], tmp_path: Path, field: str, value: object
) -> None:
    assert evidence_errors(PublicationReceipt.model_validate(native_case), tmp_path) == []
    ref = native_case["fresh_readback"]["report"]
    report = json.loads((tmp_path / ref["path"]).read_text())
    report["files"][0][field] = value
    bind_full_corpus_files(tmp_path, native_case, report["files"])
    rebind_readback(tmp_path, native_case, report)
    assert evidence_errors(PublicationReceipt.model_validate(native_case), tmp_path) == [
        "invalid_canonical_readback_proof"
    ]


def test_extra_readback_provenance_rejected_after_rebinding(
    native_case: dict[str, Any], tmp_path: Path
) -> None:
    ref = native_case["fresh_readback"]["report"]
    report = json.loads((tmp_path / ref["path"]).read_text())
    report["files"][0]["unsubstantiated_provenance"] = "claimed"
    rebind_readback(tmp_path, native_case, report)
    assert evidence_errors(PublicationReceipt.model_validate(native_case), tmp_path) == [
        "invalid_canonical_readback_proof"
    ]


@pytest.mark.parametrize(
    "malformation",
    [
        "duplicate_ids",
        "missing_id",
        "missing_files",
        "null",
        "dict",
        "string",
        "number",
        "nonobjects",
    ],
)
def test_malformed_latest_full_corpus_files_fail_closed(
    native_case: dict[str, Any], tmp_path: Path, malformation: str
) -> None:
    assert evidence_errors(PublicationReceipt.model_validate(native_case), tmp_path) == []
    ref = native_case["full_corpus_reports"][-1]
    document = json.loads((tmp_path / ref["path"]).read_text())
    if malformation == "duplicate_ids":
        document["files"].append(dict(document["files"][0]))
    elif malformation == "missing_id":
        del document["files"][0]["id"]
    elif malformation == "missing_files":
        del document["files"]
    else:
        document["files"] = {
            "null": None,
            "dict": {"first": document["files"][0]},
            "string": "not a file list",
            "number": 2,
            "nonobjects": ["first", "second"],
        }[malformation]
    write_proof(tmp_path, ref, document)
    assert evidence_errors(PublicationReceipt.model_validate(native_case), tmp_path) == [
        "invalid_canonical_readback_proof"
    ]

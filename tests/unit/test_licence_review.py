"""Tests for the fail-closed licence review queue."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from reimburse_atlas.data_dictionary import build_data_dictionary
from reimburse_atlas.licence_review import (
    build_licence_review_queue,
    write_licence_review_queue,
)
from reimburse_atlas.licence_review_validation import validate_licence_review_queue
from reimburse_atlas.publication import (
    PublicationArtifact,
    PublicationManifest,
    build_publication_manifest,
)
from scripts.reconcile_licence_decisions import reconcile


def _manifest() -> PublicationManifest:
    return PublicationManifest(
        project="test",
        manifest_version="v1",
        artifact_count=1,
        artifacts=(
            PublicationArtifact(
                table_name="example",
                relative_path="data/derived/example.csv",
                file_format="csv",
                row_count=1,
                byte_size=3,
                checksum_sha256="a" * 64,
                publication_scope="public_derived_candidate",
                licence_gate="public_reuse_review",
                contains_raw_source_payload=False,
                notes="review",
            ),
        ),
        warnings=(),
    )


def test_queue_never_infers_approval() -> None:
    """Generated rows must stay pending even for a valid candidate."""
    rows = build_licence_review_queue(_manifest())
    assert len(rows) == 1
    assert rows[0].review_status == "pending"
    assert rows[0].reviewer == ""
    assert rows[0].decision_evidence == ""


def test_project_owned_metadata_does_not_enter_source_rights_queue() -> None:
    """Apache-licensed operational metadata is not a provider-rights candidate."""
    artifact = PublicationArtifact(
        table_name="release_gates",
        relative_path="data/derived/release_readiness/release_gates.jsonl",
        file_format="jsonl",
        row_count=1,
        byte_size=2,
        checksum_sha256="a" * 64,
        publication_scope="project_owned_metadata",
        licence_gate="apache_2_0_project_output",
        contains_raw_source_payload=False,
        notes="Project output",
    )
    manifest = PublicationManifest("project", "v1", 1, (artifact,), ())

    assert build_licence_review_queue(manifest) == []


def test_research_package_descriptors_are_project_owned(repo_root: Path) -> None:
    """Package descriptors inherit neither payload rights nor source licences."""
    manifest = build_publication_manifest(root=repo_root)
    descriptors = [
        row for row in manifest.artifacts if "data/derived/research_package/" in row.relative_path
    ]

    assert descriptors
    assert {row.licence_gate for row in descriptors} == {"apache_2_0_project_output"}


def test_local_quality_reports_are_project_owned(repo_root: Path) -> None:
    """Environment-specific harness reports must not require provider-rights review."""
    manifest = build_publication_manifest(root=repo_root)
    reports = [
        row
        for row in manifest.artifacts
        if "data/derived/local_quality_gates/" in row.relative_path
    ]

    assert reports
    assert {row.licence_gate for row in reports} == {"apache_2_0_project_output"}


def test_queue_writes_checksum_bound_outputs(tmp_path: Path) -> None:
    """Queue output preserves the candidate checksum and fail-closed summary."""
    paths = write_licence_review_queue(
        build_licence_review_queue(_manifest()),
        output_dir=tmp_path / "licence_review",
    )
    payload = json.loads(paths[3].read_text(encoding="utf-8"))
    assert payload["pending_count"] == 1
    assert payload["approved_count"] == 0
    assert payload["approval_mutation_allowed"] is False
    assert '"checksum_sha256": "' + "a" * 64 in paths[0].read_text(encoding="utf-8")
    batches = paths[2].read_text(encoding="utf-8")
    assert "public_reuse_review" in batches
    assert "0,1,0,public_reuse_review,1,public_derived_candidate,0," in batches
    assert "not an approval record" in paths[4].read_text(encoding="utf-8")
    assert "Required decision fields" in paths[5].read_text(encoding="utf-8")
    assert '"\n' not in paths[4].read_text(encoding="utf-8")


def test_reviewer_packet_reports_companion_ledger_without_mutating_queue(
    tmp_path: Path,
) -> None:
    """The human packet exposes unresolved hashes while generated rows stay neutral."""
    root = tmp_path
    decision_dir = root / "data" / "licence_review"
    decision_dir.mkdir(parents=True)
    checksum = "b" * 64
    (decision_dir / "decisions.jsonl").write_text(
        json.dumps({"decision": "approved", "relative_path": "approved.csv"})
        + "\n"
        + json.dumps({
            "decision": "blocked",
            "relative_path": "blocked.csv",
            "checksum_sha256": checksum,
        })
        + "\n",
        encoding="utf-8",
    )
    paths = write_licence_review_queue(
        build_licence_review_queue(_manifest()),
        output_dir=root / "data" / "derived" / "licence_review",
        root=root,
    )
    packet = paths[5].read_text(encoding="utf-8")
    assert "1 approved" in packet
    assert "1 blocked" in packet
    assert "`blocked.csv`" in packet
    assert "`pending` by design" in packet


def test_data_dictionary_marks_queue_internal(repo_root: Path) -> None:
    """The queue is excluded to prevent a publication-manifest cycle."""
    rows = build_data_dictionary(root=repo_root)
    queue_rows = [row for row in rows if "licence_review" in row.relative_path]
    assert not queue_rows


def test_decision_schema_documents_all_required_human_fields(repo_root: Path) -> None:
    """The committed reviewer schema stays aligned with the fail-closed contract."""
    schema_path = repo_root / "data" / "licence_review" / "decision.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "review_id",
        "relative_path",
        "checksum_sha256",
        "decision",
        "reviewer",
        "reviewed_at",
        "source_terms",
        "attribution",
        "redistribution_permission",
        "restrictions",
        "evidence",
    }
    assert schema["properties"]["decision"]["enum"] == ["approved", "blocked"]


def test_validator_rejects_stale_candidate_checksum(tmp_path: Path) -> None:
    """A queue row cannot silently outlive the candidate it describes."""
    candidate = tmp_path / "data/derived/example.csv"
    candidate.parent.mkdir(parents=True)
    candidate.write_text("new\n", encoding="utf-8")
    queue = tmp_path / "queue.jsonl"
    queue.write_text(
        json.dumps({
            "review_id": "review_1",
            "relative_path": "data/derived/example.csv",
            "checksum_sha256": "0" * 64,
            "review_status": "pending",
        })
        + "\n",
        encoding="utf-8",
    )
    errors = validate_licence_review_queue(queue, root=tmp_path)
    assert any("checksum mismatch" in error for error in errors)


def test_validator_requires_complete_human_decision(tmp_path: Path) -> None:
    """Recorded decisions must contain the evidence needed for accountable review."""
    candidate = tmp_path / "data/derived/example.csv"
    candidate.parent.mkdir(parents=True)
    candidate.write_text("ok\n", encoding="utf-8")
    checksum = hashlib.sha256(candidate.read_bytes()).hexdigest()
    queue = tmp_path / "queue.jsonl"
    queue.write_text(
        json.dumps({
            "review_id": "review_1",
            "relative_path": "data/derived/example.csv",
            "checksum_sha256": checksum,
            "review_status": "pending",
        })
        + "\n",
        encoding="utf-8",
    )
    decisions = tmp_path / "decisions.jsonl"
    decisions.write_text(
        json.dumps({
            "review_id": "review_1",
            "relative_path": "data/derived/example.csv",
            "checksum_sha256": checksum,
            "decision": "approved",
            "reviewer": "A reviewer",
            "reviewed_at": "2026-07-16",
        })
        + "\n",
        encoding="utf-8",
    )
    errors = validate_licence_review_queue(queue, root=tmp_path, decisions_path=decisions)
    assert any("missing fields" in error for error in errors)


def test_validator_rejects_malformed_queue_rows_and_decisions(tmp_path: Path) -> None:
    """Defensive queue validation covers malformed paths, statuses and decisions."""
    candidate = tmp_path / "data/derived/example.csv"
    candidate.parent.mkdir(parents=True)
    candidate.write_text("ok\n", encoding="utf-8")
    checksum = hashlib.sha256(candidate.read_bytes()).hexdigest()
    queue = tmp_path / "queue.jsonl"
    queue.write_text(
        "not-json\n"
        + json.dumps({"relative_path": "data/derived/example.csv"})
        + "\n"
        + json.dumps({
            "review_id": "review_1",
            "relative_path": "missing.csv",
            "checksum_sha256": checksum,
            "review_status": "unknown",
        })
        + "\n"
        + json.dumps({
            "review_id": "review_2",
            "relative_path": "../outside.csv",
            "checksum_sha256": checksum,
            "review_status": "pending",
            "reviewer": "unexpected",
        })
        + "\n",
        encoding="utf-8",
    )
    decisions = tmp_path / "decisions.jsonl"
    decisions.write_text(
        json.dumps({"review_id": "unknown", "relative_path": "x"}) + "\n",
        encoding="utf-8",
    )
    errors = validate_licence_review_queue(queue, root=tmp_path, decisions_path=decisions)
    assert any("invalid JSON" in error for error in errors)
    assert any("review_id is required" in error for error in errors)
    assert any("candidate file missing" in error for error in errors)
    assert any("invalid review_status" in error for error in errors)
    assert any("path escapes" in error for error in errors)
    assert any("pending rows" in error for error in errors)
    assert any("missing fields" in error for error in errors)


def test_validator_accepts_complete_block_decision(tmp_path: Path) -> None:
    """A complete blocked decision is accepted when it matches the queue checksum."""
    candidate = tmp_path / "data/derived/example.csv"
    candidate.parent.mkdir(parents=True)
    candidate.write_text("ok\n", encoding="utf-8")
    checksum = hashlib.sha256(candidate.read_bytes()).hexdigest()
    queue = tmp_path / "queue.jsonl"
    queue.write_text(
        json.dumps({
            "review_id": "review_1",
            "relative_path": "data/derived/example.csv",
            "checksum_sha256": checksum,
            "review_status": "pending",
        })
        + "\n",
        encoding="utf-8",
    )
    fields = {
        "review_id": "review_1",
        "relative_path": "data/derived/example.csv",
        "checksum_sha256": checksum,
        "decision": "blocked",
        "reviewer": "A reviewer",
        "reviewed_at": "2026-07-16",
        "source_terms": "Official terms",
        "attribution": "Provider",
        "redistribution_permission": "Not granted",
        "restrictions": "No redistribution",
        "evidence": "docs/SOURCE_LICENCE_EVIDENCE.md",
    }
    decisions = tmp_path / "decisions.jsonl"
    decisions.write_text(json.dumps(fields) + "\n", encoding="utf-8")
    assert validate_licence_review_queue(queue, root=tmp_path, decisions_path=decisions) == []


def test_reconcile_adds_block_for_new_queue_candidate(tmp_path: Path) -> None:
    """New candidates must enter the ledger as blocked, not disappear."""
    candidate = tmp_path / "infra" / "metadata.json"
    candidate.parent.mkdir(parents=True)
    candidate.write_text('{"license":"other"}\n', encoding="utf-8")
    checksum = hashlib.sha256(candidate.read_bytes()).hexdigest()
    queue_dir = tmp_path / "data" / "derived" / "licence_review"
    queue_dir.mkdir(parents=True)
    (queue_dir / "licence_review_queue.jsonl").write_text(
        json.dumps({
            "review_id": "review_new",
            "relative_path": "infra/metadata.json",
            "checksum_sha256": checksum,
            "review_status": "pending",
        })
        + "\n",
        encoding="utf-8",
    )
    decisions_path = tmp_path / "data" / "licence_review" / "decisions.jsonl"
    decisions_path.parent.mkdir(parents=True)
    decisions_path.write_text("", encoding="utf-8")

    assert reconcile(tmp_path) == 1
    decision = json.loads(decisions_path.read_text(encoding="utf-8"))
    assert decision["relative_path"] == "infra/metadata.json"
    assert decision["checksum_sha256"] == checksum
    assert decision["decision"] == "blocked"
    assert (
        validate_licence_review_queue(
            queue_dir / "licence_review_queue.jsonl",
            root=tmp_path,
            decisions_path=decisions_path,
        )
        == []
    )

"""Tests for the fail-closed licence review queue."""

from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.data_dictionary import build_data_dictionary
from reimburse_atlas.licence_review import (
    build_licence_review_queue,
    write_licence_review_queue,
)
from reimburse_atlas.publication import PublicationArtifact, PublicationManifest


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


def test_queue_writes_checksum_bound_outputs(tmp_path: Path) -> None:
    """Queue output preserves the candidate checksum and fail-closed summary."""
    paths = write_licence_review_queue(
        build_licence_review_queue(_manifest()),
        output_dir=tmp_path / "licence_review",
    )
    payload = json.loads(paths[2].read_text(encoding="utf-8"))
    assert payload["pending_count"] == 1
    assert payload["approved_count"] == 0
    assert payload["approval_mutation_allowed"] is False
    assert '"checksum_sha256": "' + "a" * 64 in paths[0].read_text(encoding="utf-8")
    assert "not an approval record" in paths[3].read_text(encoding="utf-8")


def test_data_dictionary_marks_queue_internal(repo_root: Path) -> None:
    """The review queue is documented without becoming a public candidate."""
    rows = build_data_dictionary(root=repo_root)
    queue_rows = [row for row in rows if "licence_review" in row.relative_path]
    assert queue_rows
    assert all(row.publication_scope == "internal_governance" for row in queue_rows)
    assert all(row.licence_gate == "not_for_publication" for row in queue_rows)

"""Build a deterministic, fail-closed licence review queue."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.publication import PublicationManifest, build_publication_manifest
from reimburse_atlas.registry import project_root


@dataclass(frozen=True)
class LicenceReviewRecord:
    """One candidate artefact awaiting source-specific licence review."""

    review_id: str
    relative_path: str
    checksum_sha256: str
    byte_size: int
    publication_scope: str
    licence_gate: str
    contains_raw_source_payload: bool
    review_status: str
    reviewer: str
    reviewed_at: str
    decision_evidence: str
    restrictions: str


def build_licence_review_queue(
    manifest: PublicationManifest | None = None,
    *,
    root: Path | None = None,
) -> list[LicenceReviewRecord]:
    """Build pending review rows without inferring or persisting approval."""
    candidate = manifest or build_publication_manifest(root=root)
    rows: list[LicenceReviewRecord] = []
    for artifact in sorted(candidate.artifacts, key=lambda item: item.relative_path):
        digest = hashlib.sha256(artifact.relative_path.encode("utf-8")).hexdigest()[:16]
        rows.append(
            LicenceReviewRecord(
                review_id=f"licence_review_{digest}",
                relative_path=artifact.relative_path,
                checksum_sha256=artifact.checksum_sha256,
                byte_size=artifact.byte_size,
                publication_scope=artifact.publication_scope,
                licence_gate=artifact.licence_gate,
                contains_raw_source_payload=artifact.contains_raw_source_payload,
                review_status="pending",
                reviewer="",
                reviewed_at="",
                decision_evidence="",
                restrictions="",
            )
        )
    return rows


def write_licence_review_queue(
    rows: list[LicenceReviewRecord],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path, Path]:
    """Write queue rows, summary and reviewer instructions."""
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = [asdict(row) for row in rows]
    jsonl_path = write_jsonl(payload, output_dir / "licence_review_queue.jsonl")
    csv_path = write_csv(payload, output_dir / "licence_review_queue.csv")
    summary = {
        "schema_version": "licence-review-queue-v1",
        "artifact_count": len(rows),
        "review_required_count": sum(row.licence_gate != "permissive_candidate" for row in rows),
        "pending_count": sum(row.review_status == "pending" for row in rows),
        "approved_count": sum(row.review_status == "approved" for row in rows),
        "blocked_count": sum(row.review_status == "blocked" for row in rows),
        "all_approved": bool(rows) and all(row.review_status == "approved" for row in rows),
        "approval_mutation_allowed": False,
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    readme_path = output_dir / "README.md"
    readme_path.write_text(
        """# Licence review queue

This generated queue is a review aid, not an approval record. Every row remains
`pending` when regenerated. A human reviewer must record the decision, source terms,
attribution, redistribution permission, restrictions and evidence in
`docs/REVIEW_DECISIONS.md` before any publication gate can change.

The checksums bind review to the exact candidate artefacts. Do not edit this generated
queue to simulate approval, and do not publish it as evidence that review occurred.
""",
        encoding="utf-8",
    )
    return jsonl_path, csv_path, summary_path, readme_path


def build_and_write_licence_review_queue(
    *,
    root: Path | None = None,
) -> tuple[Path, Path, Path, Path]:
    """Build and write the repository's current licence review queue."""
    repo = root or project_root()
    rows = build_licence_review_queue(root=repo)
    return write_licence_review_queue(rows, output_dir=repo / "data" / "derived" / "licence_review")


def summary_as_dict(rows: list[LicenceReviewRecord]) -> dict[str, Any]:
    """Return the queue summary without writing files."""
    return {
        "artifact_count": len(rows),
        "pending_count": sum(row.review_status == "pending" for row in rows),
        "approved_count": sum(row.review_status == "approved" for row in rows),
        "blocked_count": sum(row.review_status == "blocked" for row in rows),
    }

"""Build a deterministic, fail-closed licence review queue."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from operator import itemgetter
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
    root: Path | None = None,
) -> tuple[Path, Path, Path, Path, Path, Path]:
    """Write queue rows, grouped batches, summary and reviewer instructions."""
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = [asdict(row) for row in rows]
    jsonl_path = write_jsonl(payload, output_dir / "licence_review_queue.jsonl")
    csv_path = write_csv(payload, output_dir / "licence_review_queue.csv")
    batch_keys = sorted(
        {(row.licence_gate, row.publication_scope) for row in rows},
        key=itemgetter(0, 1),
    )
    batches: list[dict[str, object]] = []
    for licence_gate, publication_scope in batch_keys:
        batch_rows = [
            row
            for row in rows
            if row.licence_gate == licence_gate and row.publication_scope == publication_scope
        ]
        batches.append({
            "licence_gate": licence_gate,
            "publication_scope": publication_scope,
            "artifact_count": len(batch_rows),
            "pending_count": sum(row.review_status == "pending" for row in batch_rows),
            "approved_count": sum(row.review_status == "approved" for row in batch_rows),
            "blocked_count": sum(row.review_status == "blocked" for row in batch_rows),
            "total_byte_size": sum(row.byte_size for row in batch_rows),
            "raw_payload_count": sum(row.contains_raw_source_payload for row in batch_rows),
            "review_action": "Human review required before publication consideration",
        })
    batch_path = write_csv(batches, output_dir / "licence_review_batches.csv")
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
    decision_path = (root or output_dir.parent.parent) / "data" / "licence_review" / "decisions.jsonl"
    decisions: list[dict[str, Any]] = []
    if decision_path.exists():
        decisions = [
            json.loads(line)
            for line in decision_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    decision_counts = {
        decision: sum(row.get("decision") == decision for row in decisions)
        for decision in ("approved", "blocked")
    }
    blocked_rows = [row for row in decisions if row.get("decision") == "blocked"]
    packet_path = output_dir / "reviewer_packet.md"
    batch_lines = "\n".join(
        f"- `{batch['licence_gate']}` / `{batch['publication_scope']}`: "
        f"{batch['artifact_count']} artefacts, {batch['total_byte_size']} bytes"
        for batch in batches
    )
    packet_path.write_text(
        """# Licence review packet

This generated packet is a checklist for an accountable human reviewer. It does not
grant approval, alter the publication manifest, or enable remote publication. Review
the exact candidate file and checksum in `licence_review_queue.csv`, then record one
complete decision row in the human decision record specified by
`docs/REVIEW_DECISIONS.md`. Use the grouped questions in
`docs/LICENCE_DECISION_MATRIX.md` to organise review, but do not replace the
checksum-bound row-level record.

## Current batches

"""
        + (batch_lines or "- No candidate artefacts are present.")
        + f"""

Total candidate artefacts: {len(rows)}; generated queue rows remain `pending` by design.

## Decision ledger snapshot

The companion checksum-bound ledger currently records **{decision_counts['approved']} approved**
and **{decision_counts['blocked']} blocked** decisions. These counts are informational;
they do not change generated queue rows or authorize publication.

### Blocked rows requiring re-review

"""
        + (
            "\n".join(
                f"- `{row.get('relative_path')}` — `{row.get('checksum_sha256')}`"
                for row in sorted(blocked_rows, key=lambda item: str(item.get("relative_path", "")))
            )
            or "- None recorded."
        )
        + """

## Required decision fields

Each decision must include `review_id`, `relative_path`, `checksum_sha256`, `decision`
(`approved` or `blocked`), `reviewer`, `reviewed_at`, `source_terms`, `attribution`,
`redistribution_permission`, `restrictions`, and `evidence`.

## Review sequence

1. Confirm the candidate checksum still matches the local file.
2. Read the applicable provider terms and record the exact evidence location.
3. Record attribution and redistribution restrictions, including any source-specific terms.
4. Choose `approved` only when redistribution is permitted for this exact candidate;
   otherwise choose `blocked`.
5. Run `pixi run licence-review-validate` and retain the output with the handoff.

The queue is regenerated from the publication manifest. Never edit generated queue rows to
simulate a decision and never treat a passing validator as a substitute for human review.
""",
        encoding="utf-8",
    )
    return jsonl_path, csv_path, batch_path, summary_path, readme_path, packet_path


def build_and_write_licence_review_queue(
    *,
    root: Path | None = None,
) -> tuple[Path, Path, Path, Path, Path, Path]:
    """Build and write the repository's current licence review queue."""
    repo = root or project_root()
    rows = build_licence_review_queue(root=repo)
    return write_licence_review_queue(
        rows,
        output_dir=repo / "data" / "derived" / "licence_review",
        root=repo,
    )


def summary_as_dict(rows: list[LicenceReviewRecord]) -> dict[str, Any]:
    """Return the queue summary without writing files."""
    return {
        "artifact_count": len(rows),
        "pending_count": sum(row.review_status == "pending" for row in rows),
        "approved_count": sum(row.review_status == "approved" for row in rows),
        "blocked_count": sum(row.review_status == "blocked" for row in rows),
    }

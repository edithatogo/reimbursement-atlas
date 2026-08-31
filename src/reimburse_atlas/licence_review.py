"""Build a deterministic, fail-closed licence review queue."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import date
from operator import itemgetter
from pathlib import Path
from typing import Annotated, Any, Literal
from urllib.parse import parse_qsl, urlsplit

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StringConstraints,
    ValidationError,
    field_validator,
)

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.publication import PublicationManifest, build_publication_manifest
from reimburse_atlas.registry import project_root

# Reviewed complete filename families from the historical PBS inventories.
# Only case and numeric runs vary; inventory additions never authorize themselves.
PBS_RAW_FILENAME_FAMILIES = frozenset({
    "#-#-#--chemotherapy-booklet.pdf",
    "#-#-#-addendum.pdf",
    "#-#-#-chemotherapy-book.pdf",
    "#-#-#-chemotherapy-booklet-erratum.pdf",
    "#-#-#-chemotherapy-booklet.pdf",
    "#-#-#-chemotherapy-erratum.pdf",
    "#-#-#-consolidated-schedules.pdf",
    "#-#-#-data-erratum.pdf",
    "#-#-#-dental-book-soc.pdf",
    "#-#-#-dental-book.pdf",
    "#-#-#-efc-errata.pdf",
    "#-#-#-efc-erratum-docetaxel.pdf",
    "#-#-#-efc-erratum.pdf",
    "#-#-#-efc-schedule-addendum.pdf",
    "#-#-#-efc-schedule-soc.pdf",
    "#-#-#-efc-schedule.pdf",
    "#-#-#-efc-soc.pdf",
    "#-#-#-efc-summary-of-changes.pdf",
    "#-#-#-efc.pdf",
    "#-#-#-efficient-funding-of-chemotherapy-erratum.pdf",
    "#-#-#-efficient-funding-of-chemotherapy.pdf",
    "#-#-#-errata-#-pricing-of-fluticasone-propionate-with-formoterol.pdf",
    "#-#-#-errata-general-schedule.pdf",
    "#-#-#-errata-notes.pdf",
    "#-#-#-errata.pdf",
    "#-#-#-erratum-blinatumomab-restriction.pdf",
    "#-#-#-erratum.pdf",
    "#-#-#-general-schedule-errata.pdf",
    "#-#-#-general-schedule-erratum-risedronate.pdf",
    "#-#-#-general-schedule-erratum.pdf",
    "#-#-#-general-schedule-r#-volume-#.pdf",
    "#-#-#-general-schedule-soc-addendum.pdf",
    "#-#-#-general-schedule-soc.pdf",
    "#-#-#-general-schedule-vol-#.pdf",
    "#-#-#-general-schedule-volume-#.pdf",
    "#-#-#-general-schedule.pdf",
    "#-#-#-general-soc.pdf",
    "#-#-#-general-volume-#.pdf",
    "#-#-#-hsd-schedule.pdf",
    "#-#-#-main-soc.pdf",
    "#-#-#-pbs-general-schedule.pdf",
    "#-#-#-pbs-schedule-approved-pharmacists.pdf",
    "#-#-#-pbs-schedule-medical-practitioners.pdf",
    "#-#-#-pbs-schedule.pdf",
    "#-#-#-pbs-summary-of-changes.pdf",
    "#-#-#-rpbs-schedule.pdf",
    "#-#-#-section#-schedule-vol-#.pdf",
    "#-#-#-section#-volume-#.pdf",
    "#-efc-soc.pdf",
    "addendum-#-september-#-benzathine-benzylpenicillin.pdf",
    "addendum-for-#-#-#.pdf",
    "errata-error-in-methylphenidate-listings-#-january-#.pdf",
    "errata-for-#-#-#-abemaciclib.pdf",
    "errata-for-#-#-#-migalastat-and-price-amoxicillin-with-clavulanic-acid.pdf",
    "errata-for-#-#-#.pdf",
    "#-#-#-chemotherapy-extracts.zip",
    "#-#-#-chemotherapy-xml.zip",
    "#-#-#-efc-extracts.zip",
    "#-#-#-efc-xml.zip",
    "#-#-#-efficient-funding-of-chemotherapy-extracts.zip",
    "#-#-#-efficient-funding-of-chemotherapy-xml.zip",
    "#-#-#-extracts-down-converted.zip",
    "#-#-#-extracts.zip",
    "#-#-#-general-schedule-ascii.zip",
    "#-#-#-general-schedule-xml.zip",
    "#-#-#-pbs-api-csv-files.zip",
    "#-#-#-pbs-api-csv.zip",
    "#-#-#-v#-down-converted-release-#.zip",
    "#-#-#-v#-down-converted.zip",
    "#-#-#-v#extracts-r#.zip",
    "#-#-#-v#extracts-release-#.zip",
    "#-#-#-v#extracts.zip",
    "#-#-#-v#soextracts-r#.zip",
    "#-#-#-v#soextracts-release-#.zip",
    "#-#-#-v#soextracts-supply-only.zip",
    "#-#-#-v#soextracts.zip",
    "#-#-#-xml-v#-down-converted.zip",
    "#-#-#-xml-v#-release-#.zip",
    "#-#-#-xml-v#.zip",
    "#-#-#-xml.zip",
    "#-supply-only-listings-july-#-public.csv",
    "supply-only-listings-dec-#-public.csv",
    "supply-only-listings-nov-#-public.csv",
})


class PBSRawPermission(BaseModel):
    """Complete owner attestation; never a publisher grant or publication receipt."""

    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal["pbs-raw-permission-v2"]
    source_id: Literal["au_pbs"]
    decision: Literal["allow_raw_redistribution"]
    permission_basis: Literal["owner_attestation"]
    permission_status: Literal["active"]
    revoked_at: None
    accountable_party: Literal["repository-owner"]
    recorded_at: date
    owner_statements: Annotated[
        list[Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]], Field(min_length=2)
    ]
    scope: Literal[
        "Raw PBS schedule PDFs and machine-readable schedule packages, "
        "including historical editions and source-identified archived variants."
    ]
    per_file_owner_approval_required: StrictBool = Field(json_schema_extra={"const": False})
    publisher_permission_document_verified: StrictBool = Field(json_schema_extra={"const": False})
    licence_identifier: None
    preservation_controls: tuple[
        Literal["Preserve original bytes, notices, attribution and source disclaimers."],
        Literal["Record source URL, retrieval evidence, edition identity, size and checksum."],
        Literal[
            "Keep source payloads out of the software Git repository; "
            "use governed external archive storage."
        ],
        Literal["Do not apply the software Apache-2.0 licence to PBS payloads."],
    ]
    exclusions: tuple[
        Literal["Non-PBS sources"],
        Literal["Credentials"],
        Literal["Papers and preprints"],
        Literal["Unsupported research claims"],
    ]
    publication_state: Literal["not_asserted"]

    @field_validator("per_file_owner_approval_required", "publisher_permission_document_verified")
    @classmethod
    def require_false(cls, value: bool) -> bool:
        """This attestation requires neither new approvals nor claimed publisher verification."""
        if value:
            message = "Owner attestation flags must remain false."
            raise ValueError(message)
        return value


def _unique_permission_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject ambiguous objects before JSON parsing can conceal revocation."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            message = "Duplicate permission record key."
            raise ValueError(message)
        result[key] = value
    return result


def pbs_raw_permission_status(*, root: Path | None = None) -> str:
    """Validate the entire active permission record independently of any artefact."""
    path = (root or project_root()) / "data/licence_review/pbs_raw_permission.json"
    try:
        content = path.read_text(encoding="utf-8")
        json.loads(content, object_pairs_hook=_unique_permission_keys)
        # Preserve strict JSON date/tuple semantics after checking key uniqueness.
        PBSRawPermission.model_validate_json(content)
    except OSError, ValueError, ValidationError:
        return "blocked_pending_explicit_permission"
    return "allowed_owner_attested_permission"


def pbs_raw_redistribution_status(source_url: str, *, root: Path | None = None) -> str:
    """Limit permission to schedule artefact paths and categories, not whole PBS hosts."""
    try:
        parsed = urlsplit(source_url)
        port = parsed.port
    except ValueError:
        return "outside_pbs_permission_scope"
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.hostname
        not in {"pbs.gov.au", "www.pbs.gov.au", "m.pbs.gov.au", "data.pbs.gov.au"}
        or parsed.username is not None
        or parsed.password is not None
        or port not in {None, 80, 443}
    ):
        return "outside_pbs_permission_scope"
    if parsed.fragment or any(
        key != "variant" or value != "3"
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
    ):
        return "outside_pbs_permission_scope"
    match = re.fullmatch(
        r"/publication/schedule/(?:[0-9]{4}(?:/[0-9]{2})?|1951-2002)/"
        r"([A-Za-z0-9_-]+)\.(pdf|zip|xml|txt|csv)",
        parsed.path,
        re.IGNORECASE,
    )
    if match is None:
        return "outside_pbs_permission_scope"
    filename = ".".join(match.groups()).lower()
    if re.sub(r"[0-9]+", "#", filename) not in PBS_RAW_FILENAME_FAMILIES:
        return "outside_pbs_permission_scope"
    return pbs_raw_permission_status(root=root)


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


def _read_decision_ledger(
    root: Path | None,
    output_dir: Path,
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    """Read the optional companion ledger for reviewer-only packet context."""
    decision_path = (
        (root or output_dir.parent.parent) / "data" / "licence_review" / "decisions.jsonl"
    )
    if not decision_path.exists():
        return {"approved": 0, "blocked": 0}, []
    decisions = [
        json.loads(line)
        for line in decision_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    counts = {
        decision: sum(row.get("decision") == decision for row in decisions)
        for decision in ("approved", "blocked")
    }
    return counts, [row for row in decisions if row.get("decision") == "blocked"]


def _effective_decisions(
    rows: list[LicenceReviewRecord],
    *,
    root: Path | None,
    output_dir: Path,
) -> dict[str, str]:
    """Return current checksum-matched decisions keyed by review identifier."""
    decision_path = (
        (root or output_dir.parent.parent) / "data" / "licence_review" / "decisions.jsonl"
    )
    if not decision_path.is_file():
        return {}
    current = {(row.review_id, row.relative_path, row.checksum_sha256) for row in rows}
    effective: dict[str, str] = {}
    for line in decision_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        decision = json.loads(line)
        identity = (
            decision.get("review_id"),
            decision.get("relative_path"),
            decision.get("checksum_sha256"),
        )
        if identity in current and decision.get("decision") in {"approved", "blocked"}:
            effective[str(decision["review_id"])] = str(decision["decision"])
    return effective


def build_licence_review_queue(
    manifest: PublicationManifest | None = None,
    *,
    root: Path | None = None,
) -> list[LicenceReviewRecord]:
    """Build pending review rows without inferring or persisting approval."""
    candidate = manifest or build_publication_manifest(root=root)
    rows: list[LicenceReviewRecord] = []
    for artifact in sorted(candidate.artifacts, key=lambda item: item.relative_path):
        if artifact.licence_gate == "apache_2_0_project_output":
            continue
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


def write_licence_review_queue(  # ruff:ignore[too-many-locals]
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
    effective_decisions = _effective_decisions(rows, root=root, output_dir=output_dir)
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
        batch_statuses = [effective_decisions.get(row.review_id, "pending") for row in batch_rows]
        pending_count = batch_statuses.count("pending")
        blocked_count = batch_statuses.count("blocked")
        batches.append({
            "licence_gate": licence_gate,
            "publication_scope": publication_scope,
            "artifact_count": len(batch_rows),
            "pending_count": pending_count,
            "approved_count": batch_statuses.count("approved"),
            "blocked_count": blocked_count,
            "total_byte_size": sum(row.byte_size for row in batch_rows),
            "raw_payload_count": sum(row.contains_raw_source_payload for row in batch_rows),
            "review_action": (
                "Accountable review required before publication consideration"
                if pending_count or blocked_count
                else "No new approval required for current checksums"
            ),
        })
    batch_path = write_csv(batches, output_dir / "licence_review_batches.csv")
    effective_statuses = [effective_decisions.get(row.review_id, "pending") for row in rows]
    summary = {
        "schema_version": "licence-review-queue-v1",
        "artifact_count": len(rows),
        "review_required_count": sum(row.licence_gate != "permissive_candidate" for row in rows),
        "queue_pending_count": effective_statuses.count("pending"),
        "pending_count": effective_statuses.count("pending"),
        "approved_count": effective_statuses.count("approved"),
        "blocked_count": effective_statuses.count("blocked"),
        "all_approved": bool(rows) and all(status == "approved" for status in effective_statuses),
        "approval_mutation_allowed": False,
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    readme_path = output_dir / "README.md"
    readme_path.write_text(
        """# Licence review queue

This generated queue is a review aid, not an approval record. Its row-level
`review_status` field remains neutral when regenerated; effective current-checksum
decisions are reported in the summary and batch files. Only rows with an effective
`pending` or `blocked` state require accountable action under
`docs/APPROVAL_POLICY.md` and `docs/REVIEW_DECISIONS.md`.

The checksums bind review to the exact candidate artefacts. Do not edit this generated
queue to simulate approval, and do not publish it as evidence that review occurred.
""",
        encoding="utf-8",
    )
    decision_counts, blocked_rows = _read_decision_ledger(root, output_dir)
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

Total candidate artefacts: {len(rows)}. Neutral generated row markers are not approval
requests; the batch and summary `pending_count` values identify required decisions.

## Decision ledger snapshot

The companion checksum-bound ledger currently records **{decision_counts["approved"]} approved**
and **{decision_counts["blocked"]} blocked** decisions. These counts are informational;
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

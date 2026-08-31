"""Offline, non-promoting contract for parent-attested PBS publication evidence."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, Self, cast
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, model_validator

SHA256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Revision = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
PositiveInt = Annotated[int, Field(gt=0)]
CANONICAL_RECEIPTS = (
    "data/derived/historical_sources/pbs_archive_v1/historical_source_downloads.jsonl",
    "data/derived/historical_sources/pbs_structured_archive_v1/historical_source_downloads.jsonl",
    "data/derived/historical_sources/pbs_archive_verification_v1/internet_archive_variant_receipts.jsonl",
)


class ContractModel(BaseModel):
    """Reject unknown fields and numeric/boolean coercions."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Evidence(ContractModel):
    """A retained metadata artefact, never raw payload bytes or an absolute path."""

    path: str
    sha256: SHA256

    @model_validator(mode="after")
    def safe_reference(self) -> Self:
        """Keep evidence references inside repository-relative metadata storage."""
        if (
            not self.path.startswith(("data/local/", "data/derived/", "data/licence_review/"))
            or "\\" in self.path
            or any(part in {"", ".", ".."} for part in self.path.split("/"))
        ):
            message = "unsafe evidence reference"
            raise ValueError(message)
        return self


class BatchProof(ContractModel):
    """Parent verification at one immutable HF revision and one staged manifest."""

    revision: Revision
    manifest_sha256: SHA256
    payload_count: PositiveInt
    payload_bytes: PositiveInt
    artifact_count: PositiveInt
    report: Evidence


class FreshReadback(BatchProof):
    """Separate fresh-download provenance and successful canonical CLI readback."""

    download_report: Evidence
    origin: Literal["independent_fresh_fixed_revision_download"]
    all_payload_hashes_verified: bool
    exact_inventory_verified: bool
    canonical_bound_readback_verified: bool
    permission_and_readme_verified: bool


class MetadataReconciliation(ContractModel):
    """Explicit bounded exception, not a false 24/24 nonraw parity claim."""

    revision: Revision
    baseline_revision: Revision
    report: Evidence
    original_strict_failure: Evidence
    status: Literal["bounded_reconciliation_pass"]
    exception_path: Literal[".gitattributes"]
    added_exact_lfs_rules: PositiveInt
    lfs_payloads: PositiveInt
    regular_payloads: PositiveInt
    nonraw_total: PositiveInt
    nonraw_byte_identical: PositiveInt
    original_attribute_bytes_preserved: bool
    only_expected_raw_lfs_rules_added: bool
    nonraw_effective_attributes_preserved: bool
    regular_payloads_not_marked_lfs: bool
    eight_configs_and_root_card_unchanged: bool


class CloseoutDelivery(ContractModel):
    """Later integration facts; preparation must not manufacture these receipts."""

    pr802_merge: Revision
    pr804_merge: Revision
    validated_commit: Revision
    validation_report: Evidence


class PublicationReceipt(ContractModel):
    """A claim validated against supplied facts; never an automatic promotion."""

    schema_version: Literal["pbs-source-publication-receipt-v1"]
    publication_state: Literal["not_asserted", "published_verified"]
    repo_id: Literal["edithatogo/reimbursement-atlas"]
    archive_prefix: Literal["raw/pbs"]
    source_merge: Revision
    source_delivery_evidence: Evidence | None
    upload_revision: Revision
    payload_count: PositiveInt
    payload_bytes: PositiveInt
    manifest_sha256: SHA256
    readme_sha256: SHA256
    permission: Evidence
    selection: Evidence
    canonical_receipts: list[Evidence]
    full_corpus_reports: list[Evidence]
    historical_completeness_asserted: bool
    retained_omissions: list[str]
    remote_inventory: BatchProof | None
    metadata_reconciliation: MetadataReconciliation | None
    fresh_readback: FreshReadback | None
    viewer_status: Literal["external_pending", "available", "unavailable", "not_checked"]
    viewer_causal_claim: Literal["none"]
    viewer_observation: Evidence | None = None
    viewer_observed_at: str | None = None
    viewer_revision_pinned: bool = False
    closeout_delivery: CloseoutDelivery | None

    def publication_blockers(self) -> list[str]:
        """Viewer service availability is deliberately not a raw-byte gate."""
        blockers: list[str] = []
        if self.source_delivery_evidence is None:
            blockers.append("source_delivery_evidence_missing")
        for name in ("remote_inventory", "metadata_reconciliation", "fresh_readback"):
            if getattr(self, name) is None:
                blockers.append(f"{name}_missing")
        return blockers

    @model_validator(mode="after")
    def coherent_claim(self) -> Self:
        """Reject contradictory, partial, or differently revisioned success claims."""
        invalid = (
            sorted(row.path for row in self.canonical_receipts) != sorted(CANONICAL_RECEIPTS)
            or len(self.full_corpus_reports) < 2
            or len({row.path for row in self.full_corpus_reports}) != len(self.full_corpus_reports)
            or self.historical_completeness_asserted
            or sorted(self.retained_omissions)
            != ["december_1987_rpbs_not_acquired", "updated_pbs_text_files_notice_excluded"]
        )
        for proof in (self.remote_inventory, self.fresh_readback):
            if proof is not None:
                invalid |= (
                    proof.revision != self.upload_revision
                    or proof.manifest_sha256 != self.manifest_sha256
                    or proof.payload_count != self.payload_count
                    or proof.payload_bytes != self.payload_bytes
                    or proof.artifact_count != self.payload_count + 2
                )
        metadata = self.metadata_reconciliation
        if metadata is not None:
            invalid |= (
                metadata.revision != self.upload_revision
                or metadata.lfs_payloads + metadata.regular_payloads != self.payload_count
                or metadata.added_exact_lfs_rules > metadata.lfs_payloads
                or metadata.nonraw_byte_identical != metadata.nonraw_total - 1
                or not all((
                    metadata.original_attribute_bytes_preserved,
                    metadata.only_expected_raw_lfs_rules_added,
                    metadata.nonraw_effective_attributes_preserved,
                    metadata.regular_payloads_not_marked_lfs,
                    metadata.eight_configs_and_root_card_unchanged,
                ))
            )
        if self.fresh_readback is not None:
            invalid |= not all((
                self.fresh_readback.all_payload_hashes_verified,
                self.fresh_readback.exact_inventory_verified,
                self.fresh_readback.canonical_bound_readback_verified,
                self.fresh_readback.permission_and_readme_verified,
            ))
        if invalid or (
            self.publication_state == "published_verified"
            and (
                self.publication_blockers()
                or any(ref.path.startswith("data/local/") for ref in self.evidence())
            )
        ):
            message = "incomplete or inconsistent PBS publication evidence"
            raise ValueError(message)
        return self

    def evidence(self) -> list[Evidence]:
        """Collect all referenced metadata artefacts for local checksum verification."""
        rows = [
            self.permission,
            self.selection,
            *self.canonical_receipts,
            *self.full_corpus_reports,
        ]
        if self.source_delivery_evidence is not None:
            rows.append(self.source_delivery_evidence)
        if self.remote_inventory is not None:
            rows.append(self.remote_inventory.report)
        if self.metadata_reconciliation is not None:
            rows.extend([
                self.metadata_reconciliation.report,
                self.metadata_reconciliation.original_strict_failure,
            ])
        if self.fresh_readback is not None:
            rows.extend([self.fresh_readback.report, self.fresh_readback.download_report])
        if self.closeout_delivery is not None:
            rows.append(self.closeout_delivery.validation_report)
        if self.viewer_observation is not None:
            rows.append(self.viewer_observation)
        return rows


def unique_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject ambiguous duplicate JSON keys at every nesting level."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            message = "duplicate JSON key"
            raise ValueError(message)
        result[key] = value
    return result


def load_receipt(path: Path) -> PublicationReceipt:
    """Read a receipt without changing its publication state."""
    return PublicationReceipt.model_validate(
        json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
    )


def evidence_digest(root: Path, ref: Evidence) -> str:
    """Hash a regular metadata file without following symlink components."""
    path = root
    for part in ref.path.split("/"):
        path /= part
        if path.is_symlink():
            message = "symlink evidence"
            raise ValueError(message)
    if not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
        message = "evidence is not a regular file"
        raise ValueError(message)
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def evidence_errors(receipt: PublicationReceipt, root: Path) -> list[str]:
    """Verify hashes AND native proof semantics without fetching raw payloads."""
    errors: list[str] = []
    documents: dict[str, Any] = {}
    for ref in receipt.evidence():
        try:
            documents[ref.path] = bound_document(root, ref)
        except OSError, ValueError, TypeError:
            errors.append(f"unreadable_evidence:{ref.path}")
            if evidence_checksum_changed(root, ref):
                errors[-1] = f"checksum_mismatch:{ref.path}"
    if errors:
        return errors
    validators = (
        ("source_delivery", source_delivery_valid),
        ("canonical_selection", canonical_selection_valid),
        ("remote_inventory", remote_inventory_valid),
        ("metadata_reconciliation", metadata_reconciliation_valid),
        ("fresh_download", fresh_download_valid),
        ("canonical_readback", canonical_readback_valid),
        ("closeout_validation", closeout_validation_valid),
        ("viewer_observation", viewer_observation_valid),
    )
    for name, validate in validators:
        try:
            valid = validate(receipt, documents)
        except KeyError, TypeError, ValueError, AttributeError:
            valid = False
        if not valid:
            errors.append(f"invalid_{name}_proof")
    return errors


def evidence_checksum_changed(root: Path, ref: Evidence) -> bool:
    """Distinguish a changed file from unreadable or malformed metadata."""
    try:
        return evidence_digest(root, ref) != ref.sha256
    except OSError, ValueError:
        return False


def reject_constant(_value: str) -> None:
    """Non-finite numbers are not JSON evidence."""
    message = "non-finite JSON number"
    raise ValueError(message)


def bound_document(root: Path, ref: Evidence) -> Any:
    """Parse the same checksum-bound bytes, rejecting non-JSON attestations."""
    # Reuse the symlink/regular-file checks; metadata files are deliberately bounded.
    evidence_digest(root, ref)
    path = root / ref.path
    if path.stat().st_size > 64 * 1024 * 1024:
        message = "oversized metadata evidence"
        raise ValueError(message)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ref.sha256:
        message = "evidence checksum mismatch"
        raise ValueError(message)
    text = raw.decode("utf-8")
    if path.suffix == ".jsonl":
        rows = [
            json.loads(line, object_pairs_hook=unique_keys, parse_constant=reject_constant)
            for line in text.splitlines()
            if line.strip()
        ]
        if not all(isinstance(row, dict) for row in rows):
            message = "non-object JSONL evidence"
            raise ValueError(message)
        return rows
    value = json.loads(text, object_pairs_hook=unique_keys, parse_constant=reject_constant)
    if not isinstance(value, dict):
        message = "non-object JSON evidence"
        raise TypeError(message)
    return cast("dict[str, Any]", value)


def same_json(left: Any, right: Any) -> bool:
    """Avoid Python's boolean/integer equality when comparing native facts."""
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def fields_match(document: Any, expected: dict[str, Any]) -> bool:
    """Require every named field, including explicit false/zero values."""
    return isinstance(document, dict) and all(
        key in document and same_json(document[key], value) for key, value in expected.items()
    )


def source_delivery_valid(receipt: PublicationReceipt, docs: dict[str, Any]) -> bool:
    """Consume the native gh PR result, not an arbitrary passed report."""
    if receipt.source_delivery_evidence is None:
        return True
    row = docs[receipt.source_delivery_evidence.path]
    checks = row.get("statusCheckRollup")
    if not isinstance(checks, list):
        return False
    typed_checks = cast("list[Any]", checks)
    return (
        fields_match(row, {"state": "MERGED", "mergeCommit": {"oid": receipt.source_merge}})
        and bool(row.get("mergedAt"))
        and bool(typed_checks)
        and all(
            fields_match(check, {"status": "COMPLETED", "conclusion": "SUCCESS"})
            or fields_match(check, {"state": "SUCCESS"})
            for check in typed_checks
        )
    )


def canonical_selection_valid(receipt: PublicationReceipt, docs: dict[str, Any]) -> bool:
    """Bind selected full rows and retain the two full-corpus failure reports."""
    canonical: dict[str, Any] = {}
    for ref in receipt.canonical_receipts:
        for row in docs[ref.path]:
            identity = row.get("id")
            if not isinstance(identity, str) or identity in canonical:
                return False
            canonical[identity] = row
    selected = docs[receipt.selection.path]
    if len(selected) != receipt.payload_count or len({row.get("id") for row in selected}) != len(
        selected
    ):
        return False
    if not all(same_json(canonical.get(row.get("id")), row) for row in selected):
        return False
    return all(
        docs[ref.path].get("schema_version")
        in {"pbs-raw-archive-staging-v1", "pbs-raw-archive-staging-v2"}
        and fields_match(
            docs[ref.path],
            {
                "mode": "dry_run",
                "status": "blocked",
                "publication_state": "not_asserted",
            },
        )
        and bool(docs[ref.path].get("errors"))
        and docs[ref.path]["coverage"]["requested_receipts"] == len(canonical)
        for ref in receipt.full_corpus_reports
    )


def remote_inventory_valid(receipt: PublicationReceipt, docs: dict[str, Any]) -> bool:
    """Accept only raw inventory facts; preserve the native overall strict failure."""
    if receipt.remote_inventory is None:
        return True
    row = docs[receipt.remote_inventory.report.path]
    return fields_match(
        row,
        {
            "schema_version": "pbs-remote-metadata-verification-v1",
            "verification_kind": "remote_metadata_only",
            "repo_id": receipt.repo_id,
            "revision": receipt.upload_revision,
            "expected_raw_count": receipt.payload_count + 2,
            "missing_raw": [],
            "raw_content_metadata_mismatch": [],
            "unexpected_files": [],
            "missing_nonraw": [],
            "status": "fail",
            "changed_nonraw": [".gitattributes"],
            "failure_codes": ["changed_nonraw", "card_metadata_mismatch"],
        },
    )


def metadata_reconciliation_valid(receipt: PublicationReceipt, docs: dict[str, Any]) -> bool:
    """Require the actual bounded exception report and its preserved failed receipt."""
    proof = receipt.metadata_reconciliation
    if proof is None:
        return True
    row = docs[proof.report.path]
    if (
        receipt.remote_inventory is None
        or proof.original_strict_failure != receipt.remote_inventory.report
    ):
        return False
    expected_checks = (
        "added_paths_exactly_equal_uncovered_expected_lfs_files",
        f"all_{proof.lfs_payloads}_lfs_objects_have_correct_effective_attributes",
        "all_8_explicit_config_paths_present_and_unchanged",
        f"all_{proof.regular_payloads}_regular_objects_not_marked_lfs",
        "all_added_lines_exact_lfs_filter_diff_merge_text_rule",
        "all_added_paths_manifest_allowlisted",
        "all_added_paths_remote_lfs_objects",
        f"exactly_{proof.nonraw_byte_identical}_nonraw_files_identical_by_blob_size_lfs_metadata",
        "manifest_and_archive_readme_attributes_unchanged",
        "nonraw_effective_attributes_unchanged",
        "only_gitattributes_nonraw_bytes_changed",
        "original_attribute_bytes_preserved_as_exact_prefix",
        "parsed_card_data_unchanged",
        "regular_object_attributes_unchanged",
        "root_readme_exact_bytes_unchanged",
    )
    exception = row.get("technical_exception", {})
    paths = exception.get("added_paths", [])
    return (
        fields_match(
            row,
            {
                "schema_version": "pbs-additive-lfs-reconciliation-v1",
                "status": proof.status,
                "repo_id": receipt.repo_id,
                "archive_revision": receipt.upload_revision,
                "baseline_revision": proof.baseline_revision,
                "baseline_nonraw_count": proof.nonraw_total,
                "nonraw_byte_identical_count": proof.nonraw_byte_identical,
                "exact_24_of_24_nonraw_parity_claimed": False,
                "original_strict_receipt_preserved": True,
                "original_strict_receipt_sha256": proof.original_strict_failure.sha256,
                "original_strict_verification_status": "fail",
                "original_strict_failure_codes": ["changed_nonraw", "card_metadata_mismatch"],
                "raw_inventory_status": "pass_at_archive_revision_in_original_receipt",
            },
        )
        and fields_match(row.get("checks"), dict.fromkeys(expected_checks, True))
        and fields_match(
            exception,
            {
                "file": ".gitattributes",
                "added_exact_raw_lfs_rules": proof.added_exact_lfs_rules,
                "removed_or_changed_original_bytes": 0,
            },
        )
        and len(paths) == len(set(paths)) == proof.added_exact_lfs_rules
        and all(path.startswith("raw/pbs/payloads/") and path.endswith(".pdf") for path in paths)
        and fields_match(row.get("card"), {"parsed_card_exact": True, "root_readme_exact": True})
    )


def fresh_download_valid(receipt: PublicationReceipt, docs: dict[str, Any]) -> bool:
    """Consume the native proof derived from actual HF cache metadata inventory."""
    proof = receipt.fresh_readback
    if proof is None:
        return True
    if proof.report.path == proof.download_report.path:
        return False
    row = docs[proof.download_report.path]
    digest = row.get("metadata_inventory_sha256")
    return (
        isinstance(digest, str)
        and len(digest) == 64
        and all(char in "0123456789abcdef" for char in digest)
        and fields_match(
            row,
            {
                "schema_version": "pbs-fresh-download-v1",
                "status": "verified",
                "origin": "independent_fresh_fixed_revision_download",
                "repo_id": receipt.repo_id,
                "revision": receipt.upload_revision,
                "download_exit_code": 0,
                "force_download": True,
                "xet_disabled": True,
                "include_prefix": "raw/pbs/",
                "metadata_count": receipt.payload_count + 2,
                "all_metadata_revisions_match": True,
                "exact_metadata_inventory": True,
                "payload_count": receipt.payload_count,
                "payload_bytes": receipt.payload_bytes,
                "artifact_count": receipt.payload_count + 2,
                "manifest_sha256": receipt.manifest_sha256,
                "canonical_readback_performed_by_this_script": False,
            },
        )
    )


def canonical_file_fields(source: dict[str, Any], selected: dict[str, Any]) -> dict[str, Any]:
    """Derive public identity fields without trusting a parent-filled readback row."""
    variant = "official_source_url" in source
    parent = selected[source["source_id"]] if variant else source
    if parent["source_id"] != "au_pbs":
        message = "non-PBS canonical parent"
        raise ValueError(message)
    url = source["official_source_url" if variant else "source_url"]
    if not isinstance(url, str):
        message = "canonical URL must be text"
        raise TypeError(message)
    url_path = PurePosixPath(urlsplit(url).path)
    filename = url_path.name
    if parent.get("file_name", filename) != filename:
        message = "canonical filename mismatch"
        raise ValueError(message)
    expected = {
        "id": source["id"],
        "source_id": "au_pbs",
        "source_version_id": parent["source_version_id"],
        "citation_key": parent["citation_key"],
        "source_url": url,
        "original_source_filename": filename,
        "byte_size": source["byte_size"],
        "checksum_sha256": source["checksum_sha256"],
        "acquisition_status": source["status"],
        "archive_path": (
            f"raw/pbs/payloads/{source['id']}/{source['checksum_sha256']}{url_path.suffix.lower()}"
        ),
    }
    if variant:
        stamp, replay = source["archive_timestamp"], source["archive_replay_url"]
        prefix = f"https://web.archive.org/web/{stamp}id_/"
        if not isinstance(replay, str) or not replay.startswith(prefix):
            message = "canonical replay identity mismatch"
            raise ValueError(message)
        original = replay[len(prefix) :]
        official = url.split("?", maxsplit=1)[0]
        expected.update(
            archive_timestamp=stamp,
            archive_replay_url=replay,
            archive_original_url=original,
            archive_identity_basis="exact_replay_url",
        )
        if original != official:
            captured, publisher = urlsplit(original), urlsplit(official)
            if (
                captured.scheme == publisher.scheme
                or publisher._replace(scheme=captured.scheme) != captured
                or source["archive_checksum_sha1_base32"] != source["checksum_sha1_base32"]
            ):
                message = "canonical CDX identity mismatch"
                raise ValueError(message)
            expected.update(
                archive_identity_basis="exact_cdx_capture_and_payload_digests",
                archive_cdx_digest_sha1_base32=source["archive_checksum_sha1_base32"],
            )
    return expected


def canonical_readback_valid(receipt: PublicationReceipt, docs: dict[str, Any]) -> bool:
    """Verify native readback results and reconstruct the exact staged manifest binding."""
    proof = receipt.fresh_readback
    if proof is None:
        return True
    row = docs[proof.report.path]
    raw_files = row.get("files", [])
    if not isinstance(raw_files, list):
        return False
    files = cast("list[dict[str, Any]]", raw_files)
    if len(files) != receipt.payload_count:
        return False
    selected = {item["id"]: item for item in docs[receipt.selection.path]}
    # The superseding full-corpus report also binds CDX-derived identity fields.
    # Preserve all of its row fields, not merely the payload digest and size.
    corpus_rows = cast("list[dict[str, Any]]", docs[receipt.full_corpus_reports[-1].path]["files"])
    corpus = {item["id"]: item for item in corpus_rows}
    if (
        len(corpus) != len(corpus_rows)
        or set(selected) != {file["id"] for file in files}
        or not all(
            fields_match(file, canonical_file_fields(selected[file["id"]], selected))
            and same_json(file, corpus.get(file["id"]))
            for file in files
        )
    ):
        return False
    if any(type(file.get("byte_size")) is not int or file["byte_size"] <= 0 for file in files):
        return False
    stage_bytes = (json.dumps({**row, "mode": "stage"}, indent=2, sort_keys=True) + "\n").encode()
    return (
        fields_match(
            row,
            {
                "schema_version": "pbs-raw-archive-staging-v2",
                "status": "verified",
                "mode": "readback",
                "archive_prefix": "raw/pbs",
                "errors": [],
                "publication_state": "not_asserted",
                "network_publication_performed": False,
                "archive_readme_checksum_sha256": receipt.readme_sha256,
                "permission_record": receipt.permission.path,
                "permission_record_checksum_sha256": receipt.permission.sha256,
            },
        )
        and fields_match(
            row.get("coverage"),
            {
                "requested_receipts": receipt.payload_count,
                "verified_files": receipt.payload_count,
                "failed_receipts": 0,
                "failed_operations": 0,
                "complete_for_requested_batch": True,
                "historical_completeness_asserted": False,
            },
        )
        and sum(file["byte_size"] for file in files) == receipt.payload_bytes
        and len({file["id"] for file in files}) == receipt.payload_count
        and len({file["archive_path"] for file in files}) == receipt.payload_count
        and hashlib.sha256(stage_bytes).hexdigest() == receipt.manifest_sha256
    )


def closeout_validation_valid(receipt: PublicationReceipt, docs: dict[str, Any]) -> bool:
    """Require an exact-commit validation envelope, never reuse an inventory receipt."""
    proof = receipt.closeout_delivery
    if proof is None:
        return True
    row = docs[proof.validation_report.path]
    quality = row.get("local_quality", {})
    count = quality.get("gate_count")
    return (
        fields_match(
            row,
            {
                "schema_version": "pbs-closeout-validation-v1",
                "status": "pass",
                "validated_commit": proof.validated_commit,
                "pr802_merge": proof.pr802_merge,
                "pr804_merge": proof.pr804_merge,
                "regeneration_fixed_point_verified": True,
            },
        )
        and type(count) is int
        and count > 0
        and fields_match(
            quality,
            {
                "schema_version": "local-quality-gates-v1",
                "profile": "ci",
                "passed": count,
                "failed": 0,
                "blocked_network": 0,
                "missing_tool": 0,
                "timed_out": 0,
                "wrong_tool": 0,
                "skipped": 0,
                "blocking_failures": 0,
            },
        )
    )


def viewer_observation_valid(receipt: PublicationReceipt, docs: dict[str, Any]) -> bool:
    """Bind a dated availability claim without turning availability into a raw gate."""
    if receipt.viewer_observation is None:
        return receipt.viewer_status != "available"
    row = docs[receipt.viewer_observation.path]
    configs = [
        "acquisition_b1",
        "catalogue_b0",
        "evidence_b2",
        "gold",
        "lineage",
        "platinum",
        "promotion_decisions",
        "silver",
    ]
    if receipt.viewer_observed_at is None:
        return False
    observed = datetime.fromisoformat(receipt.viewer_observed_at)
    return (
        observed.tzinfo is not None
        and receipt.viewer_status == "available"
        and fields_match(
            row,
            {
                "schema_version": "pbs-viewer-observation-v1",
                "status": "completed",
                "repo_id": receipt.repo_id,
                "completed_at": receipt.viewer_observed_at,
                "viewer_revision_pinned": receipt.viewer_revision_pinned,
                "viewer_discovery_cleared": True,
                "discovered_configs": configs,
                "pending_configs": [],
                "failed_configs": [],
                "remote_mutations_performed": False,
            },
        )
        and fields_match(
            row.get("viewer_validity"),
            dict.fromkeys(("viewer", "preview", "search", "filter", "statistics"), True),
        )
        and fields_match(
            row.get("parquet_summary"),
            {
                "http_status": 200,
                "file_count": 8,
                "listed_configs": configs,
                "pending": [],
                "failed": [],
                "partial": False,
            },
        )
        and set(row.get("first_rows_summary", {})) == set(configs)
        and all(
            fields_match(
                row["first_rows_summary"][config], {"http_status": 200, "error_code": None}
            )
            for config in configs
        )
    )

"""Deterministic projections of repository evidence into medallion layers."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

from pydantic import HttpUrl

from reimburse_atlas.medallion import (
    BronzeAcquisitionReceipt,
    BronzeEvidenceRecord,
    BronzeSourceIndexRecord,
    MedallionArtifactRecord,
    MedallionPromotionDecision,
    PlatinumReleaseContract,
    RightsState,
)
from reimburse_atlas.registry import project_root

GENERATED_AT = "1970-01-01T00:00:00Z"


@dataclass(frozen=True)
class MedallionProjectionSummary:
    """Counts and fail-closed readiness for generated medallion evidence."""

    schema_version: str
    bronze_b0_count: int
    bronze_b1_count: int
    bronze_b2_count: int
    silver_count: int
    silver_approved_count: int
    gold_count: int
    gold_approved_count: int
    platinum_count: int
    platinum_approved_count: int
    blocked_promotion_count: int
    medallion_contract_ready: bool
    evidence_release_ready: bool


def _read_json(path: Path) -> dict[str, Any]:
    return cast("dict[str, Any]", json.loads(path.read_text(encoding="utf-8")))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [
        cast("dict[str, Any]", json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _row_sha256(row: dict[str, Any]) -> str:
    payload = json.dumps(row, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(payload).hexdigest()


def _rights_state(value: object) -> RightsState:
    mapping: dict[str, RightsState] = {
        "permissive": "permissive",
        "permissive_candidate": "permissive",
        "public_reuse_review": "public_reuse_review",
        "restricted": "restricted_local_only",
        "restricted_or_licence_review": "restricted_local_only",
        "restricted_local_only": "restricted_local_only",
        "metadata_only": "metadata_only",
    }
    return mapping.get(str(value), "public_reuse_review")


def _approved_checksums(root: Path) -> set[tuple[str, str]]:
    return {
        (str(row.get("relative_path")), str(row.get("checksum_sha256")))
        for row in _read_jsonl(root / "data/licence_review/decisions.jsonl")
        if row.get("decision") == "approved"
    }


def _reviewed_snapshot_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    bundle_root = root / "data/derived/reviewed_source_bundles"
    for path in sorted(bundle_root.glob("*/source_snapshots.jsonl")):
        rows.extend(_read_jsonl(path))
    return rows


def _historical_acquisition_rows(root: Path) -> tuple[list[dict[str, Any]], str]:
    output = root / "data/derived/historical_sources"
    rows = _read_jsonl(output / "historical_source_downloads.jsonl")
    summary_path = output / "historical_source_downloads_summary.json"
    summary = _read_json(summary_path) if summary_path.is_file() else {}
    return rows, str(summary.get("generated_at", GENERATED_AT))


def _build_bronze_source_index(
    sources: list[dict[str, Any]],
    files: list[dict[str, Any]],
    validations: dict[str, dict[str, Any]],
) -> list[BronzeSourceIndexRecord]:
    files_by_source: dict[str, list[dict[str, Any]]] = {}
    for source_file in files:
        files_by_source.setdefault(str(source_file["source_id"]), []).append(source_file)
    records: list[BronzeSourceIndexRecord] = []
    for source in sorted(sources, key=lambda row: str(row["id"])):
        source_files = files_by_source.get(str(source["id"]), [])
        acquired = any(
            len(str(validations.get(str(row["id"]), {}).get("checksum_sha256", ""))) == 64
            for row in source_files
        )
        records.append(
            BronzeSourceIndexRecord(
                source_id=str(source["id"]),
                source_version_id=f"catalog_{source['id']}",
                authoritative_locator=HttpUrl(str(source["primary_url"])),
                expected_media_types=tuple(
                    part.strip() for part in str(source["format"]).split("/") if part.strip()
                ),
                rights_state=_rights_state(
                    source_files[0].get("licence_gate") if source_files else "public_reuse_review"
                ),
                credential_state=(
                    "required" if any(row.get("auth_env_var") for row in source_files) else "none"
                ),
                indexed_at=GENERATED_AT,
                acquisition_status="acquired" if acquired else "not_attempted",
                notes="B0 catalogue identity; presence does not imply acquisition or coverage.",
            )
        )
    return records


def build_bronze_projections(  # ruff: ignore[too-many-locals] - coordinates three typed receipt lanes
    root: Path,
) -> tuple[
    list[BronzeSourceIndexRecord],
    list[BronzeAcquisitionReceipt],
    list[BronzeEvidenceRecord],
]:
    """Project source declarations and validation evidence into B0/B1/B2."""
    sources = _read_jsonl(root / "data/seed/source_registry.jsonl")
    files = _read_jsonl(root / "data/seed/source_files.jsonl")
    validations = {
        str(row["source_file_id"]): row
        for row in _read_jsonl(
            root / "data/derived/source_validation/source_content_validation.jsonl"
        )
    }
    b0 = _build_bronze_source_index(sources, files, validations)
    b1: list[BronzeAcquisitionReceipt] = []
    b2: list[BronzeEvidenceRecord] = []
    b2_checksums: set[str] = set()

    def append_evidence(
        *,
        acquisition_id: str,
        source_id: str,
        source_version_id: str,
        source_url: str,
        checksum: str,
        byte_size: int,
        rights: RightsState,
        verified_at: str,
        notes: str,
    ) -> None:
        if checksum in b2_checksums:
            return
        b2_checksums.add(checksum)
        b2.append(
            BronzeEvidenceRecord(
                evidence_id=f"evidence:sha256:{checksum}",
                acquisition_id=acquisition_id,
                source_id=source_id,
                source_version_id=source_version_id,
                evidence_kind="rights_constrained_reference",
                payload_sha256=checksum,
                byte_size=byte_size,
                immutable_locator=f"sha256:{checksum}",
                source_locator=HttpUrl(source_url),
                rights_state=rights,
                fixity_verified_at=verified_at,
                notes=notes,
            )
        )

    for source_file in sorted(files, key=lambda row: str(row["id"])):
        validation = validations.get(str(source_file["id"]))
        checksum = str(validation.get("checksum_sha256")) if validation else None
        valid_checksum = checksum if checksum and len(checksum) == 64 else None
        status = str(validation.get("validation_status")) if validation else "missing"
        rights = _rights_state(source_file.get("licence_gate"))
        event_source = {
            "source_file_id": source_file["id"],
            "validation": validation,
        }
        event_digest = _row_sha256(event_source)
        acquisition_id = f"sha256:{valid_checksum or event_digest}"
        receipt = BronzeAcquisitionReceipt(
            event_id=f"event:{event_digest}",
            acquisition_id=acquisition_id,
            source_id=str(source_file["source_id"]),
            source_version_id=str(source_file["source_version_id"]),
            source_locator=HttpUrl(str(source_file["source_url"])),
            retrieved_at=GENERATED_AT,
            payload_sha256=valid_checksum,
            byte_size=int(validation["byte_size"]) if validation and valid_checksum else None,
            media_type=str(source_file["expected_format"]),
            outcome="acquired" if valid_checksum else "blocked",
            rights_state=rights,
            admission_state="admitted" if status == "pass" and valid_checksum else "pending",
            evidence_disposition=("rights_constrained_reference" if valid_checksum else "none"),
            notes="B1 event projected from checksum-bound source validation; raw path omitted.",
        )
        b1.append(receipt)
        if valid_checksum:
            assert validation is not None
            append_evidence(
                acquisition_id=acquisition_id,
                source_id=str(source_file["source_id"]),
                source_version_id=str(source_file["source_version_id"]),
                source_url=str(source_file["source_url"]),
                checksum=valid_checksum,
                byte_size=int(validation.get("byte_size", 0)),
                rights=rights,
                verified_at=GENERATED_AT,
                notes="B2 reference preserves identity without publishing local raw bytes.",
            )

    for snapshot in sorted(_reviewed_snapshot_rows(root), key=lambda row: str(row["id"])):
        checksum = str(snapshot.get("checksum_sha256", ""))
        valid_checksum = checksum if len(checksum) == 64 else None
        event_source = {
            key: snapshot.get(key)
            for key in (
                "id",
                "source_id",
                "source_version_id",
                "source_url",
                "retrieved_at",
                "checksum_sha256",
                "byte_size",
                "content_type",
                "licence_gate",
            )
        }
        event_digest = _row_sha256(event_source)
        acquisition_id = f"sha256:{valid_checksum or event_digest}"
        rights = _rights_state(snapshot.get("licence_gate"))
        b1.append(
            BronzeAcquisitionReceipt(
                event_id=f"event:{event_digest}",
                acquisition_id=acquisition_id,
                source_id=str(snapshot["source_id"]),
                source_version_id=str(snapshot["source_version_id"]),
                source_locator=HttpUrl(str(snapshot["source_url"])),
                retrieved_at=str(snapshot.get("retrieved_at", GENERATED_AT)),
                payload_sha256=valid_checksum,
                byte_size=int(snapshot["byte_size"]) if valid_checksum else None,
                media_type=str(snapshot.get("content_type", "application/octet-stream")),
                outcome="acquired" if valid_checksum else "failed",
                rights_state=rights,
                admission_state="admitted" if valid_checksum else "rejected",
                evidence_disposition=("rights_constrained_reference" if valid_checksum else "none"),
                notes=(
                    "B1 event projected from a reviewed source-bundle snapshot; local raw "
                    "path omitted."
                ),
            )
        )
        if valid_checksum:
            append_evidence(
                acquisition_id=acquisition_id,
                source_id=str(snapshot["source_id"]),
                source_version_id=str(snapshot["source_version_id"]),
                source_url=str(snapshot["source_url"]),
                checksum=valid_checksum,
                byte_size=int(snapshot["byte_size"]),
                rights=rights,
                verified_at=str(snapshot.get("retrieved_at", GENERATED_AT)),
                notes=(
                    "B2 reviewed-snapshot reference preserves fixity and rights state "
                    "without redistributing source bytes."
                ),
            )

    historical_rows, historical_verified_at = _historical_acquisition_rows(root)
    for historical in sorted(historical_rows, key=lambda row: str(row["id"])):
        checksum = str(historical.get("checksum_sha256") or "")
        acquired = historical.get("status") in {"downloaded", "cached"} and len(checksum) == 64
        valid_checksum = checksum if acquired else None
        event_source = {
            key: historical.get(key)
            for key in (
                "id",
                "source_id",
                "source_version_id",
                "source_url",
                "status",
                "checksum_sha256",
                "byte_size",
                "file_kind",
                "licence_gate",
                "review_status",
            )
        }
        event_digest = _row_sha256(event_source)
        acquisition_id = f"sha256:{valid_checksum or event_digest}"
        rights = _rights_state(historical.get("licence_gate"))
        b1.append(
            BronzeAcquisitionReceipt(
                event_id=f"event:{event_digest}",
                acquisition_id=acquisition_id,
                source_id=str(historical["source_id"]),
                source_version_id=str(historical["source_version_id"]),
                source_locator=HttpUrl(str(historical["source_url"])),
                retrieved_at=historical_verified_at,
                payload_sha256=valid_checksum,
                byte_size=int(historical["byte_size"]) if valid_checksum else None,
                media_type=str(historical.get("file_kind", "application/octet-stream")),
                outcome="acquired" if valid_checksum else "failed",
                rights_state=rights,
                admission_state="admitted" if valid_checksum else "rejected",
                evidence_disposition=("rights_constrained_reference" if valid_checksum else "none"),
                notes=(
                    "B1 historical acquisition receipt; ignored cache path and transfer "
                    "diagnostics omitted."
                ),
            )
        )
        if valid_checksum:
            append_evidence(
                acquisition_id=acquisition_id,
                source_id=str(historical["source_id"]),
                source_version_id=str(historical["source_version_id"]),
                source_url=str(historical["source_url"]),
                checksum=valid_checksum,
                byte_size=int(historical["byte_size"]),
                rights=rights,
                verified_at=historical_verified_at,
                notes=(
                    "B2 historical checksum reference records current-run fixity; source "
                    "bytes remain ignored and local."
                ),
            )

    acquired_sources = {row.source_id for row in b1 if row.outcome == "acquired"}
    b0 = [
        row.model_copy(
            update={
                "acquisition_status": "acquired"
                if row.source_id in acquired_sources
                else row.acquisition_status
            }
        )
        for row in b0
    ]
    b1.sort(key=lambda row: row.event_id)
    b2.sort(key=lambda row: row.evidence_id)
    return b0, b1, b2


def build_silver_artifacts(root: Path) -> list[MedallionArtifactRecord]:
    """Build Silver candidates from reviewed-source validation reports."""
    approved = _approved_checksums(root)
    records: list[MedallionArtifactRecord] = []
    bundle_root = root / "data/derived/reviewed_source_bundles"
    for path in sorted(bundle_root.glob("*/validation_report.json")):
        report = _read_json(path)
        relative = path.relative_to(root).as_posix()
        digest = _sha256(path)
        snapshots_path = path.parent / "source_snapshots.jsonl"
        snapshots = _read_jsonl(snapshots_path)
        input_ids = tuple(
            str(row.get("id") or f"sha256:{row['checksum_sha256']}") for row in snapshots
        ) or (str(report.get("snapshot_id", path.parent.name)),)
        input_sha = tuple(
            str(row["checksum_sha256"])
            for row in snapshots
            if isinstance(row.get("checksum_sha256"), str)
            and len(str(row["checksum_sha256"])) == 64
        )
        if not input_sha:
            source_checksum = str(report.get("checksum_sha256", ""))
            input_sha = (source_checksum,) if len(source_checksum) == 64 else (digest,)
        rights = _rights_state(report.get("licence_gate"))
        records.append(
            MedallionArtifactRecord(
                artifact_id=f"silver:{path.parent.name}",
                layer="silver",
                relative_path=relative,
                sha256=digest,
                contract_id="silver-source-faithful-v1",
                input_artifact_ids=input_ids,
                input_sha256=input_sha,
                generated_at=GENERATED_AT,
                rights_state=rights,
                promotion_status=(
                    "approved_within_scope" if (relative, digest) in approved else "candidate"
                ),
                notes=(
                    "Validation-report identity for a source-faithful reviewed bundle; "
                    "raw bytes omitted."
                ),
            )
        )
    registry_path = root / "data/seed/source_registry.jsonl"
    if registry_path.is_file():
        registry_digest = _sha256(registry_path)
        records.append(
            MedallionArtifactRecord(
                artifact_id="silver:source-registry",
                layer="silver",
                relative_path=registry_path.relative_to(root).as_posix(),
                sha256=registry_digest,
                contract_id="silver-source-registry-v1",
                input_artifact_ids=("source_registry",),
                input_sha256=(registry_digest,),
                generated_at=GENERATED_AT,
                rights_state="permissive",
                promotion_status="approved_within_scope",
                notes=(
                    "Source-faithful typed registry metadata; approval does not establish "
                    "acquisition, coverage or source quality."
                ),
            )
        )
    return records


def build_gold_artifacts(
    root: Path, silver: list[MedallionArtifactRecord]
) -> list[MedallionArtifactRecord]:
    """Build bounded Gold analytical artifacts from approved Silver inputs."""
    path = root / "data/derived/mapping_study/expansion_v9/evaluation_summary.json"
    records: list[MedallionArtifactRecord] = []
    mapping_inputs = [row for row in silver if row.contract_id == "silver-source-faithful-v1"]
    if path.is_file() and mapping_inputs:
        evaluation = _read_json(path)
        digest = _sha256(path)
        accepted = (
            evaluation.get("status") == "accepted" and evaluation.get("evaluated_once") is True
        )
        silver_approved = all(
            row.promotion_status == "approved_within_scope" for row in mapping_inputs
        )
        records.append(
            MedallionArtifactRecord(
                artifact_id="gold:mapping-study-expansion-v9",
                layer="gold",
                relative_path=path.relative_to(root).as_posix(),
                sha256=digest,
                contract_id="gold-adjudicated-mapping-v1",
                input_artifact_ids=tuple(row.artifact_id for row in mapping_inputs),
                input_sha256=tuple(row.sha256 for row in mapping_inputs),
                generated_at=GENERATED_AT,
                rights_state="permissive" if silver_approved else "public_reuse_review",
                promotion_status=(
                    "approved_within_scope" if accepted and silver_approved else "candidate"
                ),
                notes=(
                    "Sealed one-time holdout evidence; scope does not imply causal or "
                    "price equivalence."
                ),
            )
        )

    registry = next((row for row in silver if row.artifact_id == "silver:source-registry"), None)
    claim_path = root / "data/derived/research_claims/rq_source_transparency.json"
    review_path = root / "data/research_claims/source_transparency_review.json"
    if registry is not None and claim_path.is_file() and review_path.is_file():
        claim_digest = _sha256(claim_path)
        claim = _read_json(claim_path)
        review = _read_json(review_path)
        current_review = (
            review.get("status") == "approved_within_scope"
            and review.get("claim_package_sha256") == claim_digest
            and review.get("claim_package_path") == claim_path.relative_to(root).as_posix()
            and review.get("reviewed_derived_inputs") is True
            and review.get("analysis_validated") is True
            and claim.get("descriptive_results", {}).get("input_sha256") == registry.sha256
        )
        records.append(
            MedallionArtifactRecord(
                artifact_id="gold:source-transparency-claim-package",
                layer="gold",
                relative_path=claim_path.relative_to(root).as_posix(),
                sha256=claim_digest,
                contract_id="gold-source-transparency-metadata-v1",
                input_artifact_ids=(registry.artifact_id,),
                input_sha256=(registry.sha256,),
                generated_at=GENERATED_AT,
                rights_state="permissive",
                promotion_status=("approved_within_scope" if current_review else "candidate"),
                notes=(
                    "Accountably reviewed metadata observations only; no quality ranking, "
                    "causal, price-equivalence or coverage claim."
                ),
            )
        )
    return records


def _load_platinum_contract(root: Path) -> PlatinumReleaseContract | None:
    path = root / "data/product_release/contracts/source_transparency_dashboard.json"
    if not path.is_file():
        return None
    return PlatinumReleaseContract.model_validate(_read_json(path))


def _path_matches(root: Path, relative_path: str, expected_sha256: str) -> bool:
    path = root / relative_path
    return path.is_file() and _sha256(path) == expected_sha256


def _public_data_policy_passed(root: Path) -> bool:
    return any(
        row.get("id") == "public_data_policy"
        and row.get("status") == "passed"
        and row.get("return_code") == 0
        for row in _read_jsonl(root / "data/derived/local_quality_gates/local_quality_gates.jsonl")
    )


def _bounded_platinum_gates(
    root: Path,
    gold: list[MedallionArtifactRecord],
    *,
    repository_release_ready: bool,
) -> tuple[PlatinumReleaseContract | None, tuple[str, ...]]:
    contract = _load_platinum_contract(root)
    if contract is None:
        return None, ()
    gold_input = next((row for row in gold if row.artifact_id == contract.gold_artifact_id), None)
    passed: list[str] = []
    if gold_input is not None and gold_input.promotion_status == "approved_within_scope":
        passed.append("gold_input_approved")
    if repository_release_ready:
        passed.append("repository_release_ready")
    if _public_data_policy_passed(root):
        passed.append("public_data_policy_passed")
    if contract.rights_state == "permissive":
        passed.append("product_rights_approved")
    review_current = all((
        _path_matches(root, contract.product_path, contract.product_sha256),
        _path_matches(root, contract.source_registry_path, contract.source_registry_sha256),
        _path_matches(root, contract.claim_package_path, contract.claim_package_sha256),
        _path_matches(root, contract.claim_review_path, contract.claim_review_sha256),
    ))
    if review_current:
        review = _read_json(root / contract.claim_review_path)
        if (
            review.get("status") == "approved_within_scope"
            and review.get("claim_package_sha256") == contract.claim_package_sha256
        ):
            passed.append("scoped_claim_review_current")
    return contract, tuple(passed)


def build_platinum_artifacts(
    root: Path,
    gold: list[MedallionArtifactRecord],
    *,
    evidence_release_ready: bool,
    repository_release_ready: bool = False,
) -> list[MedallionArtifactRecord]:
    """Build Platinum products while keeping bounded and global gates distinct."""
    if not gold:
        return []
    product_paths = (
        Path("pyproject.toml"),
        Path("apps/dashboard/src/pages/sources/index.astro"),
        Path(".zenodo.json"),
    )
    contract, bounded_passed = _bounded_platinum_gates(
        root, gold, repository_release_ready=repository_release_ready
    )
    records: list[MedallionArtifactRecord] = []
    for relative_path in product_paths:
        path = root / relative_path
        if not path.is_file():
            continue
        relative = relative_path.as_posix()
        digest = _sha256(path)
        bounded = contract is not None and relative == contract.product_path
        bounded_approved = (
            bounded
            and contract is not None
            and set(contract.required_gate_ids) <= set(bounded_passed)
        )
        product_gold = (
            [row for row in gold if row.artifact_id == contract.gold_artifact_id]
            if bounded and contract is not None
            else gold
        )
        records.append(
            MedallionArtifactRecord(
                artifact_id=f"platinum:{relative.replace('/', ':')}",
                layer="platinum",
                relative_path=relative,
                sha256=digest,
                contract_id=(
                    contract.contract_id if bounded and contract else "platinum-public-product-v1"
                ),
                input_artifact_ids=tuple(row.artifact_id for row in product_gold),
                input_sha256=tuple(row.sha256 for row in product_gold),
                generated_at=GENERATED_AT,
                rights_state="permissive",
                promotion_status=(
                    "approved_within_scope"
                    if bounded_approved
                    else ("candidate" if evidence_release_ready else "blocked")
                ),
                notes=(
                    contract.approval_scope
                    if bounded and contract
                    else (
                        "Product projection only; destination state is not source truth "
                        "or publication authority."
                    )
                ),
            )
        )
    return records


def build_promotion_decisions(
    root: Path,
    b0: list[BronzeSourceIndexRecord],
    b1: list[BronzeAcquisitionReceipt],
    b2: list[BronzeEvidenceRecord],
    silver: list[MedallionArtifactRecord],
    gold: list[MedallionArtifactRecord],
    platinum: list[MedallionArtifactRecord],
    *,
    evidence_release_ready: bool,
    repository_release_ready: bool,
) -> list[MedallionPromotionDecision]:
    """Build explicit transition decisions from observed gate evidence."""
    decisions: list[MedallionPromotionDecision] = []
    b1_by_source = {row.source_id: row for row in b1 if row.outcome == "acquired"}
    b2_by_version = {row.source_version_id: row for row in b2}
    for row in b0:
        receipt = b1_by_source.get(row.source_id)
        passed = receipt is not None and receipt.outcome == "acquired"
        decisions.append(
            MedallionPromotionDecision(
                decision_id=f"promotion:b0-b1:{row.source_version_id}",
                subject_id=row.source_version_id,
                from_layer="bronze_b0",
                to_layer="bronze_b1",
                input_sha256=(_row_sha256(row.model_dump(mode="json")),),
                required_gate_ids=("acquisition_event_recorded",),
                passed_gate_ids=("acquisition_event_recorded",) if passed else (),
                status="approved" if passed else "blocked",
                decided_at=GENERATED_AT,
                reason_codes=("acquired_checksum_bound" if passed else "acquisition_missing",),
                scope_notes="B0 presence alone does not establish acquisition or coverage.",
            )
        )
    for receipt in b1:
        evidence = b2_by_version.get(receipt.source_version_id)
        passed = evidence is not None and receipt.admission_state == "admitted"
        decisions.append(
            MedallionPromotionDecision(
                decision_id=f"promotion:b1-b2:{receipt.source_version_id}",
                subject_id=receipt.acquisition_id,
                from_layer="bronze_b1",
                to_layer="bronze_b2",
                input_sha256=(
                    receipt.payload_sha256 or _row_sha256(receipt.model_dump(mode="json")),
                ),
                required_gate_ids=("fixity_verified", "admission_passed"),
                passed_gate_ids=("fixity_verified", "admission_passed") if passed else (),
                status="approved" if passed else "blocked",
                decided_at=GENERATED_AT,
                reason_codes=("immutable_reference_recorded" if passed else "b2_evidence_missing",),
                scope_notes="Approval records identity only and does not authorize redistribution.",
            )
        )
    silver_by_id = {row.artifact_id: row for row in silver}
    for gold_artifact in gold:
        gold_inputs = [silver_by_id[item] for item in gold_artifact.input_artifact_ids]
        silver_passed = all(row.promotion_status == "approved_within_scope" for row in gold_inputs)
        source_transparency = gold_artifact.contract_id == "gold-source-transparency-metadata-v1"
        required_gates = (
            ("source_registry_silver_approved", "scoped_claim_review_current")
            if source_transparency
            else ("silver_inputs_approved", "mapping_evaluation_sealed")
        )
        passed_gold_gates = (
            required_gates
            if (silver_passed and gold_artifact.promotion_status == "approved_within_scope")
            else required_gates[:1]
        )
        decisions.append(
            MedallionPromotionDecision(
                decision_id=f"promotion:silver-gold:{hashlib.sha256(gold_artifact.artifact_id.encode()).hexdigest()[:16]}",
                subject_id=gold_artifact.artifact_id,
                from_layer="silver",
                to_layer="gold",
                input_sha256=tuple(row.sha256 for row in gold_inputs),
                required_gate_ids=required_gates,
                passed_gate_ids=passed_gold_gates,
                status=(
                    "approved"
                    if silver_passed and gold_artifact.promotion_status == "approved_within_scope"
                    else "blocked"
                ),
                decided_at=GENERATED_AT,
                reason_codes=(
                    "scoped_source_transparency_evidence"
                    if source_transparency
                    and silver_passed
                    and gold_artifact.promotion_status == "approved_within_scope"
                    else "sealed_mapping_evidence"
                    if silver_passed and gold_artifact.promotion_status == "approved_within_scope"
                    else "silver_or_licence_gate_pending",
                ),
                scope_notes=(
                    "Gold scope is bounded to reviewed source-registry metadata observations."
                    if source_transparency
                    else "Gold scope is bounded to the sealed study and its documented metrics."
                ),
            )
        )
    for product in platinum:
        contract, bounded_passed = _bounded_platinum_gates(
            root, gold, repository_release_ready=repository_release_ready
        )
        bounded = contract is not None and product.contract_id == contract.contract_id
        passed = bounded and product.promotion_status == "approved_within_scope"
        passed_gates = list(bounded_passed) if bounded else ["gold_input_present"]
        if not bounded and evidence_release_ready:
            passed_gates.append("evidence_release_ready")
        if not bounded and product.rights_state == "permissive":
            passed_gates.append("product_rights_approved")
        decisions.append(
            MedallionPromotionDecision(
                decision_id=f"promotion:gold-platinum:{hashlib.sha256(product.artifact_id.encode()).hexdigest()[:16]}",
                subject_id=product.artifact_id,
                from_layer="gold",
                to_layer="platinum",
                input_sha256=product.input_sha256,
                required_gate_ids=(
                    contract.required_gate_ids
                    if bounded and contract is not None
                    else (
                        "gold_input_present",
                        "evidence_release_ready",
                        "product_rights_approved",
                    )
                ),
                passed_gate_ids=tuple(passed_gates),
                status="approved" if passed else "blocked",
                decided_at=GENERATED_AT,
                reason_codes=(
                    "bounded_source_transparency_release_contract_satisfied"
                    if passed
                    else "external_product_release_gate_separate"
                    if product.promotion_status == "candidate"
                    else "platinum_upstream_gates_pending",
                ),
                scope_notes=(
                    (
                        f"{contract.approval_scope} Prohibited: "
                        f"{', '.join(contract.prohibited_claims)}."
                    )
                    if bounded and contract is not None
                    else "External mutation and publication authority remain separate."
                ),
            )
        )
    return decisions


def _write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.with_suffix(".jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    fields = sorted({key for row in rows for key in row}) if rows else ["empty"]
    with path.with_suffix(".csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                key: json.dumps(value, sort_keys=True)
                if isinstance(value, (dict, list, tuple))
                else value
                for key, value in row.items()
            })


def materialise_medallion_projection(root: Path | None = None) -> MedallionProjectionSummary:
    """Generate all medallion evidence and return its summary."""
    from reimburse_atlas.release_readiness import build_release_readiness_report

    repo = root or project_root()
    output = repo / "data/derived/medallion"
    b0, b1, b2 = build_bronze_projections(repo)
    silver = build_silver_artifacts(repo)
    gold = build_gold_artifacts(repo, silver)
    medallion_ready = bool(b0 and b1 and b2 and silver and gold)

    # Materialise a fail-closed projection first so the canonical release model can
    # evaluate the medallion gate from current-run evidence rather than stale files.
    platinum = build_platinum_artifacts(
        repo, gold, evidence_release_ready=False, repository_release_ready=False
    )
    provisional = MedallionProjectionSummary(
        schema_version="medallion-projection-v3",
        bronze_b0_count=len(b0),
        bronze_b1_count=len(b1),
        bronze_b2_count=len(b2),
        silver_count=len(silver),
        silver_approved_count=sum(
            row.promotion_status == "approved_within_scope" for row in silver
        ),
        gold_count=len(gold),
        gold_approved_count=sum(row.promotion_status == "approved_within_scope" for row in gold),
        platinum_count=len(platinum),
        platinum_approved_count=0,
        blocked_promotion_count=0,
        medallion_contract_ready=medallion_ready,
        evidence_release_ready=False,
    )
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(
        json.dumps(asdict(provisional), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    release_summary = build_release_readiness_report(repo).summary
    evidence_ready = release_summary.evidence_release_ready
    platinum = build_platinum_artifacts(
        repo,
        gold,
        evidence_release_ready=evidence_ready,
        repository_release_ready=release_summary.repository_release_ready,
    )
    decisions = build_promotion_decisions(
        repo,
        b0,
        b1,
        b2,
        silver,
        gold,
        platinum,
        evidence_release_ready=evidence_ready,
        repository_release_ready=release_summary.repository_release_ready,
    )
    collections = {
        "bronze_source_index": b0,
        "bronze_acquisition_ledger": b1,
        "bronze_evidence": b2,
        "medallion_artifacts": [*silver, *gold, *platinum],
        "promotion_decisions": decisions,
    }
    for name, records in collections.items():
        _write_rows(output / name, [record.model_dump(mode="json") for record in records])
    summary = MedallionProjectionSummary(
        schema_version="medallion-projection-v3",
        bronze_b0_count=len(b0),
        bronze_b1_count=len(b1),
        bronze_b2_count=len(b2),
        silver_count=len(silver),
        silver_approved_count=sum(
            row.promotion_status == "approved_within_scope" for row in silver
        ),
        gold_count=len(gold),
        gold_approved_count=sum(row.promotion_status == "approved_within_scope" for row in gold),
        platinum_count=len(platinum),
        platinum_approved_count=sum(
            row.promotion_status == "approved_within_scope" for row in platinum
        ),
        blocked_promotion_count=sum(row.status == "blocked" for row in decisions),
        medallion_contract_ready=medallion_ready,
        evidence_release_ready=evidence_ready,
    )
    (output / "summary.json").write_text(
        json.dumps(asdict(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary

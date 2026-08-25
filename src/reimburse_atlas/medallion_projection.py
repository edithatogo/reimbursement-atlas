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


def _evidence_release_ready(root: Path) -> bool:
    summary = _read_json(root / "data/derived/evidence_readiness/summary.json")
    question_count = int(summary.get("research_question_count", 0))
    return (
        question_count > 0
        and int(summary.get("evidence_ready", 0)) == question_count
        and int(summary.get("blocked", 0)) == 0
    )


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


def build_bronze_projections(
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
            b2.append(
                BronzeEvidenceRecord(
                    evidence_id=f"evidence:sha256:{valid_checksum}",
                    acquisition_id=acquisition_id,
                    source_id=str(source_file["source_id"]),
                    source_version_id=str(source_file["source_version_id"]),
                    evidence_kind="rights_constrained_reference",
                    payload_sha256=valid_checksum,
                    byte_size=int(validation.get("byte_size", 0)),
                    immutable_locator=f"sha256:{valid_checksum}",
                    source_locator=HttpUrl(str(source_file["source_url"])),
                    rights_state=rights,
                    fixity_verified_at=GENERATED_AT,
                    notes="B2 reference preserves identity without publishing local raw bytes.",
                )
            )
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
    return records


def build_gold_artifacts(
    root: Path, silver: list[MedallionArtifactRecord]
) -> list[MedallionArtifactRecord]:
    """Build the Gold candidate from the sealed mapping evaluation."""
    path = root / "data/derived/mapping_study/expansion_v9/evaluation_summary.json"
    if not path.is_file() or not silver:
        return []
    evaluation = _read_json(path)
    digest = _sha256(path)
    accepted = evaluation.get("status") == "accepted" and evaluation.get("evaluated_once") is True
    silver_approved = all(row.promotion_status == "approved_within_scope" for row in silver)
    relative = path.relative_to(root).as_posix()
    return [
        MedallionArtifactRecord(
            artifact_id="gold:mapping-study-expansion-v9",
            layer="gold",
            relative_path=relative,
            sha256=digest,
            contract_id="gold-adjudicated-mapping-v1",
            input_artifact_ids=tuple(row.artifact_id for row in silver),
            input_sha256=tuple(row.sha256 for row in silver),
            generated_at=GENERATED_AT,
            rights_state="permissive" if silver_approved else "public_reuse_review",
            promotion_status="approved_within_scope"
            if accepted and silver_approved
            else "candidate",
            notes=(
                "Sealed one-time holdout evidence; scope does not imply causal or "
                "price equivalence."
            ),
        )
    ]


def build_platinum_artifacts(
    root: Path, gold: list[MedallionArtifactRecord]
) -> list[MedallionArtifactRecord]:
    """Inventory product surfaces as Platinum candidates without publication."""
    if not gold:
        return []
    product_paths = (
        Path("pyproject.toml"),
        Path("apps/dashboard/package-lock.json"),
        Path(".zenodo.json"),
    )
    records: list[MedallionArtifactRecord] = []
    evidence_ready = _evidence_release_ready(root)
    for relative_path in product_paths:
        path = root / relative_path
        if not path.is_file():
            continue
        relative = relative_path.as_posix()
        digest = _sha256(path)
        records.append(
            MedallionArtifactRecord(
                artifact_id=f"platinum:{relative.replace('/', ':')}",
                layer="platinum",
                relative_path=relative,
                sha256=digest,
                contract_id="platinum-public-product-v1",
                input_artifact_ids=tuple(row.artifact_id for row in gold),
                input_sha256=tuple(row.sha256 for row in gold),
                generated_at=GENERATED_AT,
                rights_state="permissive",
                promotion_status="candidate" if evidence_ready else "blocked",
                notes=(
                    "Product projection only; destination state is not source truth or "
                    "publication authority."
                ),
            )
        )
    return records


def build_promotion_decisions(
    b0: list[BronzeSourceIndexRecord],
    b1: list[BronzeAcquisitionReceipt],
    b2: list[BronzeEvidenceRecord],
    silver: list[MedallionArtifactRecord],
    gold: list[MedallionArtifactRecord],
    platinum: list[MedallionArtifactRecord],
    *,
    evidence_release_ready: bool,
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
    silver_passed = all(row.promotion_status == "approved_within_scope" for row in silver)
    if gold:
        decisions.append(
            MedallionPromotionDecision(
                decision_id="promotion:silver-gold:expansion-v9",
                subject_id=gold[0].artifact_id,
                from_layer="silver",
                to_layer="gold",
                input_sha256=tuple(row.sha256 for row in silver),
                required_gate_ids=("silver_inputs_approved", "mapping_evaluation_sealed"),
                passed_gate_ids=(
                    ("silver_inputs_approved", "mapping_evaluation_sealed")
                    if silver_passed and gold[0].promotion_status == "approved_within_scope"
                    else ("mapping_evaluation_sealed",)
                ),
                status=(
                    "approved"
                    if silver_passed and gold[0].promotion_status == "approved_within_scope"
                    else "blocked"
                ),
                decided_at=GENERATED_AT,
                reason_codes=(
                    "sealed_mapping_evidence"
                    if silver_passed and gold[0].promotion_status == "approved_within_scope"
                    else "silver_or_licence_gate_pending",
                ),
                scope_notes="Gold scope is bounded to the sealed study and its documented metrics.",
            )
        )
    for product in platinum:
        passed = False
        passed_gates = ["gold_input_present"]
        if evidence_release_ready:
            passed_gates.append("evidence_release_ready")
        if product.rights_state == "permissive":
            passed_gates.append("product_rights_approved")
        decisions.append(
            MedallionPromotionDecision(
                decision_id=f"promotion:gold-platinum:{hashlib.sha256(product.artifact_id.encode()).hexdigest()[:16]}",
                subject_id=product.artifact_id,
                from_layer="gold",
                to_layer="platinum",
                input_sha256=tuple(row.sha256 for row in gold),
                required_gate_ids=(
                    "gold_input_present",
                    "evidence_release_ready",
                    "product_rights_approved",
                ),
                passed_gate_ids=tuple(passed_gates),
                status="approved" if passed else "blocked",
                decided_at=GENERATED_AT,
                reason_codes=(
                    "external_product_release_gate_separate"
                    if product.promotion_status == "candidate"
                    else "platinum_upstream_gates_pending",
                ),
                scope_notes="External mutation and publication authority remain separate.",
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
    repo = root or project_root()
    output = repo / "data/derived/medallion"
    b0, b1, b2 = build_bronze_projections(repo)
    silver = build_silver_artifacts(repo)
    gold = build_gold_artifacts(repo, silver)
    platinum = build_platinum_artifacts(repo, gold)
    evidence_ready = _evidence_release_ready(repo)
    decisions = build_promotion_decisions(
        b0, b1, b2, silver, gold, platinum, evidence_release_ready=evidence_ready
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
        schema_version="medallion-projection-v1",
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
        medallion_contract_ready=bool(b0 and b1 and b2 and silver and gold),
        evidence_release_ready=evidence_ready,
    )
    (output / "summary.json").write_text(
        json.dumps(asdict(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary

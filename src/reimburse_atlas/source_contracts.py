"""Source-specific content-contract validators for reviewed local source files.

The generic source-content gate checks file existence, size, checksum and broad
format. This module adds lightweight, source-specific contracts before raw files
are allowed into reviewed-source bundle parsing. It intentionally records only
metadata and column/marker observations; it never copies raw source payloads.
"""

from __future__ import annotations

import csv
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import SourceContractValidationRecord, SourceFileRecord
from reimburse_atlas.registry import project_root
from reimburse_atlas.source_downloads import safe_local_target

SourceContractStatus = Literal["pass", "warn", "fail", "missing", "skipped"]


@dataclass(frozen=True)
class SourceContract:
    """Expected source-specific shape for one local source file."""

    name: str
    expected_columns: tuple[str, ...]
    required_markers: tuple[str, ...]
    delimiter_candidates: tuple[str, ...] = ("|", ",", "\t")
    skip_reason: str | None = None


CONTRACTS: dict[str, SourceContract] = {
    "au_mbs_20260701_imap_txt": SourceContract(
        name="MBS item-map TXT contract",
        expected_columns=("item_number", "category", "schedule_fee", "start_date"),
        required_markers=("item_number", "schedule_fee"),
    ),
    "au_mbs_20260701_desc_txt": SourceContract(
        name="MBS descriptor TXT contract",
        expected_columns=("item_number", "descriptor"),
        required_markers=("item_number", "descriptor"),
    ),
    "au_pbs_api_v3_documentation": SourceContract(
        name="PBS API/CSV extract contract",
        expected_columns=("pbs_item_code", "drug_name", "effective_date"),
        required_markers=("pbs",),
        skip_reason=(
            "Documentation/API endpoint record; validate a reviewed CSV or JSON "
            "extract instead."
        ),
    ),
    "us_cms_clfs_26clabq3_ama_zip": SourceContract(
        name="CMS CLFS AMA-gated ZIP contract",
        expected_columns=("hcpcs", "payment_rate"),
        required_markers=("26CLABQ3",),
        skip_reason="AMA-gated ZIP requires manual licence review before local validation.",
    ),
    "us_cms_asp_july_2026_payment_limit_page": SourceContract(
        name="CMS ASP payment-limit extract contract",
        expected_columns=("hcpcs_code", "payment_limit", "effective_date"),
        required_markers=("asp", "payment"),
        skip_reason=(
            "Landing-page/manual-extract record; validate the extracted local file instead."
        ),
    ),
    "us_cms_pfs_rvu26c_page": SourceContract(
        name="CMS PFS RVU extract contract",
        expected_columns=("hcpcs_code", "nonfacility_price", "facility_price"),
        required_markers=("rvu", "hcpcs"),
        skip_reason=(
            "Landing-page/manual-extract record; validate the extracted local file instead."
        ),
    ),
}


def build_source_contract_validations(
    records: list[SourceFileRecord],
    *,
    raw_dir: Path | None = None,
) -> list[SourceContractValidationRecord]:
    """Validate source-specific contracts for registered local source files."""
    base = raw_dir or project_root() / "data" / "raw_live"
    return [_validate_contract(record, base) for record in records]


def validate_path_against_contract(
    record: SourceFileRecord,
    path: Path,
) -> SourceContractValidationRecord:
    """Validate an explicit local file against the contract for a source-file record."""
    contract = _contract_for(record)
    return _validate_file(record, contract, path)


def write_source_contract_validations(
    rows: list[SourceContractValidationRecord],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write contract-validation rows and a compact summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    data = [row.model_dump(mode="json") for row in rows]
    jsonl_path = write_jsonl(data, output_dir / "source_contract_validation.jsonl")
    csv_path = write_csv(data, output_dir / "source_contract_validation.csv")
    summary = {
        "contract_count": len(rows),
        "pass": sum(row.contract_status == "pass" for row in rows),
        "warn": sum(row.contract_status == "warn" for row in rows),
        "fail": sum(row.contract_status == "fail" for row in rows),
        "missing": sum(row.contract_status == "missing" for row in rows),
        "skipped": sum(row.contract_status == "skipped" for row in rows),
        "blocking_failures": sum(row.contract_status == "fail" for row in rows),
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return jsonl_path, csv_path, summary_path


def _validate_contract(record: SourceFileRecord, raw_dir: Path) -> SourceContractValidationRecord:
    contract = _contract_for(record)
    if contract.skip_reason is not None:
        return _make_record(
            record,
            contract,
            status="skipped",
            issues=(contract.skip_reason,),
            recommended_action=(
                "Perform manual/licence review first, then validate the extracted local file."
            ),
        )
    path = safe_local_target(record, raw_dir)
    if not path.exists():
        return _make_record(
            record,
            contract,
            status="missing",
            issues=("local raw file is absent",),
            recommended_action=(
                "Run source-download-plan in a network-enabled environment, then rerun contracts."
            ),
        )
    return _validate_file(record, contract, path)


def _validate_file(
    record: SourceFileRecord,
    contract: SourceContract,
    path: Path,
) -> SourceContractValidationRecord:
    if not path.is_file():
        return _make_record(
            record,
            contract,
            status="fail",
            issues=("contract target is not a file",),
            byte_size=0,
            recommended_action="Remove the invalid local target and reacquire the source file.",
        )
    byte_size = path.stat().st_size
    if byte_size == 0:
        return _make_record(
            record,
            contract,
            status="fail",
            issues=("contract target file is empty",),
            byte_size=byte_size,
            recommended_action="Reacquire the source file before parsing.",
        )
    if path.suffix.lower() == ".zip":
        return _validate_zip(record, contract, path, byte_size)
    observed_columns = _observed_columns(path, contract.delimiter_candidates)
    observed_markers = _observed_markers(path, contract.required_markers)
    missing_columns = tuple(col for col in contract.expected_columns if col not in observed_columns)
    missing_markers = tuple(
        marker for marker in contract.required_markers if marker not in observed_markers
    )
    issues: list[str] = []
    if missing_columns:
        issues.append(f"missing expected columns: {', '.join(missing_columns)}")
    if missing_markers:
        issues.append(f"missing required markers: {', '.join(missing_markers)}")
    if _looks_like_html(path):
        issues.append("download looks like HTML rather than data")
    status = "pass" if not issues else "warn"
    if any("HTML" in issue or "html" in issue for issue in issues):
        status = "fail"
    return _make_record(
        record,
        contract,
        status=status,
        observed_columns=observed_columns,
        observed_markers=observed_markers,
        byte_size=byte_size,
        issues=tuple(issues),
        recommended_action=(
            "Proceed to reviewed-source bundle parsing."
            if status == "pass"
            else "Inspect source layout and update the contract or parser before parsing."
        ),
    )


def _validate_zip(
    record: SourceFileRecord,
    contract: SourceContract,
    path: Path,
    byte_size: int,
) -> SourceContractValidationRecord:
    if not zipfile.is_zipfile(path):
        return _make_record(
            record,
            contract,
            status="fail",
            byte_size=byte_size,
            issues=("file suffix is ZIP but archive validation failed",),
            recommended_action="Reacquire the source archive after manual licence review.",
        )
    with zipfile.ZipFile(path) as archive:
        names = tuple(archive.namelist())
    issues = () if names else ("ZIP archive is empty",)
    return _make_record(
        record,
        contract,
        status="pass" if names else "fail",
        byte_size=byte_size,
        observed_markers=names[:10],
        issues=issues,
        recommended_action=(
            "Extract into ignored local storage and validate the derived CSV/XLSX fields."
            if names
            else "Reacquire the source archive."
        ),
    )


def _contract_for(record: SourceFileRecord) -> SourceContract:
    if record.id in CONTRACTS:
        return CONTRACTS[record.id]
    if "pbs" in record.parser_hint.lower():
        return CONTRACTS["au_pbs_api_v3_documentation"]
    return SourceContract(
        name="Generic tabular source contract",
        expected_columns=(),
        required_markers=(record.source_id,),
    )


def _make_record(
    record: SourceFileRecord,
    contract: SourceContract,
    *,
    status: SourceContractStatus,
    recommended_action: str,
    required_markers: tuple[str, ...] | None = None,
    observed_markers: tuple[str, ...] = (),
    expected_columns: tuple[str, ...] | None = None,
    observed_columns: tuple[str, ...] = (),
    byte_size: int = 0,
    issues: tuple[str, ...] = (),
) -> SourceContractValidationRecord:
    return SourceContractValidationRecord(
        id=f"contract_{record.id}",
        source_file_id=record.id,
        source_id=record.source_id,
        source_version_id=record.source_version_id,
        parser_hint=record.parser_hint,
        contract_name=contract.name,
        contract_status=status,
        required_markers=(
            required_markers if required_markers is not None else contract.required_markers
        ),
        observed_markers=observed_markers,
        expected_columns=(
            expected_columns if expected_columns is not None else contract.expected_columns
        ),
        observed_columns=observed_columns,
        byte_size=byte_size,
        issues=issues,
        recommended_action=recommended_action,
    )


def _observed_columns(path: Path, delimiters: tuple[str, ...]) -> tuple[str, ...]:
    sample = path.read_text(encoding="utf-8", errors="replace").splitlines()
    first_line = next((line for line in sample if line.strip()), "")
    if not first_line:
        return ()
    delimiter = max(delimiters, key=lambda item: first_line.count(item))
    if delimiter not in first_line:
        return ()
    reader = csv.reader([first_line], delimiter=delimiter)
    try:
        columns = next(reader)
    except StopIteration:
        return ()
    return tuple(_normalise_column(column) for column in columns if column.strip())


def _observed_markers(path: Path, markers: tuple[str, ...]) -> tuple[str, ...]:
    text = path.read_text(encoding="utf-8", errors="replace")[:8192].lower()
    return tuple(marker for marker in markers if marker.lower() in text)


def _normalise_column(column: str) -> str:
    return column.strip().lower().replace(" ", "_").replace("-", "_")


def _looks_like_html(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")[:2048].lower()
    return any(marker in text for marker in ("<!doctype html", "<html", "<head"))

"""Redacted, source-specific evidence for locally cached PBS API responses."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any, cast

from pydantic import HttpUrl, TypeAdapter

from reimburse_atlas.contracts import PbsApiAcquisitionRecord
from reimburse_atlas.io import write_csv, write_jsonl

API_ROOT = "https://data-api.health.gov.au/pbs/api/v3"
SOURCE_ID = "au_pbs"
SOURCE_VERSION_ID = "au_pbs_api_v3_current_month"

ENDPOINT_COLUMNS: dict[str, tuple[str, ...]] = {
    "items": ("pbs_code", "drug_name", "schedule_code"),
    "fees": ("schedule_code",),
}


def build_pbs_api_evidence(
    schedules_path: Path,
    item_paths: tuple[Path, ...],
    fees_path: Path | None,
    *,
    schedule_code: str,
    retrieved_at: str,
) -> list[PbsApiAcquisitionRecord]:
    """Validate cached PBS responses and return metadata-only evidence rows."""
    schedule = _find_schedule(schedules_path, schedule_code)
    effective_date = _schedule_date(schedule)
    rows: list[PbsApiAcquisitionRecord] = []
    rows.append(
        _json_record(
            schedules_path,
            endpoint="schedules",
            schedule_code=schedule_code,
            effective_date=effective_date,
            retrieved_at=retrieved_at,
            page_number=1,
            required_columns=("schedule_code", "effective_date"),
        )
    )
    for page_number, path in enumerate(item_paths, start=1):
        rows.append(
            _csv_record(
                path,
                endpoint="items",
                schedule_code=schedule_code,
                effective_date=effective_date,
                retrieved_at=retrieved_at,
                page_number=page_number,
            )
        )
    if fees_path is not None:
        rows.append(
            _csv_record(
                fees_path,
                endpoint="fees",
                schedule_code=schedule_code,
                effective_date=effective_date,
                retrieved_at=retrieved_at,
                page_number=1,
            )
        )
    return rows


def write_pbs_api_evidence(
    rows: list[PbsApiAcquisitionRecord],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write JSONL, CSV and summary evidence without raw source content."""
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = [row.model_dump(mode="json") for row in rows]
    jsonl_path = write_jsonl(payload, output_dir / "pbs_api_acquisition.jsonl")
    csv_path = write_csv(payload, output_dir / "pbs_api_acquisition.csv")
    summary = {
        "record_count": len(rows),
        "endpoint_count": len({row.endpoint for row in rows}),
        "total_source_records": sum(row.record_count for row in rows),
        "schema_failures": sum(row.schema_status == "fail" for row in rows),
        "review_status": "acquired_unreviewed" if rows else "not_acquired",
        "raw_payloads_tracked": False,
    }
    summary_path = output_dir / "pbs_api_acquisition_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return jsonl_path, csv_path, summary_path


def _find_schedule(path: Path, schedule_code: str) -> dict[str, Any]:
    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    candidates = _data_array(payload, "PBS schedules response must contain a data array")
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        candidate_dict = cast("dict[str, Any]", candidate)
        value = candidate_dict.get("schedule_code", candidate_dict.get("scheduleCode"))
        if str(value) == schedule_code:
            return candidate_dict
    message = f"PBS schedule code not found: {schedule_code}"
    raise ValueError(message)


def _schedule_date(schedule: dict[str, Any]) -> date:
    value = schedule.get("effective_date", schedule.get("effectiveDate"))
    if not isinstance(value, str):
        message = "PBS schedule is missing an effective date"
        raise TypeError(message)
    return date.fromisoformat(value[:10])


def _csv_record(
    path: Path,
    *,
    endpoint: str,
    schedule_code: str,
    effective_date: date,
    retrieved_at: str,
    page_number: int,
) -> PbsApiAcquisitionRecord:
    required = ENDPOINT_COLUMNS[endpoint]
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        observed = tuple(str(field).strip() for field in (reader.fieldnames or ()) if field)
        missing = set(required) - set(observed)
        record_count = 0
        invalid_rows = 0
        for row in reader:
            record_count += 1
            if missing or any(not str(row.get(column, "")).strip() for column in required):
                invalid_rows += 1
    return _record(
        path,
        endpoint=cast("Any", endpoint),
        schedule_code=schedule_code,
        effective_date=effective_date,
        retrieved_at=retrieved_at,
        page_number=page_number,
        content_type="text/csv",
        record_count=record_count,
        required_columns=required,
        observed_columns=observed,
        invalid_row_count=invalid_rows,
    )


def _json_record(
    path: Path,
    *,
    endpoint: str,
    schedule_code: str,
    effective_date: date,
    retrieved_at: str,
    page_number: int,
    required_columns: tuple[str, ...],
) -> PbsApiAcquisitionRecord:
    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    candidates = _data_array(payload, "PBS JSON response must contain a data array")
    observed_keys: set[str] = set()
    invalid_rows = 0
    for row in candidates:
        if not isinstance(row, dict):
            invalid_rows += 1
            continue
        row_dict = cast("dict[str, Any]", row)
        observed_keys.update(str(key) for key in row_dict)
        if any(not str(row_dict.get(column, "")).strip() for column in required_columns):
            invalid_rows += 1
    observed = tuple(sorted(observed_keys))
    return _record(
        path,
        endpoint=cast("Any", endpoint),
        schedule_code=schedule_code,
        effective_date=effective_date,
        retrieved_at=retrieved_at,
        page_number=page_number,
        content_type="application/json",
        record_count=len(candidates),
        required_columns=required_columns,
        observed_columns=observed,
        invalid_row_count=invalid_rows,
    )


def _record(
    path: Path,
    *,
    endpoint: Any,
    schedule_code: str,
    effective_date: date,
    retrieved_at: str,
    page_number: int,
    content_type: str,
    record_count: int,
    required_columns: tuple[str, ...],
    observed_columns: tuple[str, ...],
    invalid_row_count: int,
) -> PbsApiAcquisitionRecord:
    checksum = _sha256(path)
    schema_status = (
        "pass"
        if not (set(required_columns) - set(observed_columns)) and not invalid_row_count
        else "fail"
    )
    return PbsApiAcquisitionRecord(
        id=f"pbs_api_{schedule_code}_{endpoint}_page_{page_number}",
        source_id=SOURCE_ID,
        source_version_id=SOURCE_VERSION_ID,
        endpoint=endpoint,
        endpoint_url=TypeAdapter(HttpUrl).validate_python(f"{API_ROOT}/{endpoint}"),
        schedule_code=schedule_code,
        effective_date=effective_date,
        page_number=page_number,
        file_name=path.name,
        local_target_ref=f"[ignored-local-raw-cache]/au_pbs/{path.name}",
        retrieved_at=retrieved_at,
        content_type=content_type,
        record_count=record_count,
        byte_size=path.stat().st_size,
        checksum_sha256=checksum,
        required_columns=required_columns,
        observed_columns=observed_columns,
        schema_status=schema_status,
        invalid_row_count=invalid_row_count,
        notes=(
            "Acquisition evidence only; raw response remains ignored and source/licence/domain "
            "review is required before derived publication."
        ),
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _data_array(payload: Any, message: str) -> list[Any]:
    """Extract and type-check the API's JSON data array."""
    if isinstance(payload, dict):
        payload_dict = cast("dict[str, Any]", payload)
        candidates: Any = payload_dict.get("data", payload_dict)
    else:
        candidates = payload
    if not isinstance(candidates, list):
        raise TypeError(message)
    return cast("list[Any]", candidates)

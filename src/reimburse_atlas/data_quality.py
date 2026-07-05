"""Generated data-quality checks for seed, derived and publication artefacts."""

from __future__ import annotations

import csv
import json
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import DataQualityCheckRecord
from reimburse_atlas.registry import project_root


def build_data_quality_checks(root: Path | None = None) -> list[DataQualityCheckRecord]:
    """Build deterministic data-quality checks across key repository artefacts."""
    repo = root or project_root()
    rows: list[DataQualityCheckRecord] = []
    rows.extend(_minimum_row_count_checks(repo))
    rows.extend(_unique_id_checks(repo))
    rows.extend(_referential_integrity_checks(repo))
    rows.extend(_generated_artifact_checks(repo))
    rows.extend(_publication_safety_checks(repo))
    return rows


def write_data_quality_checks(
    rows: list[DataQualityCheckRecord],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write data-quality check rows and summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    data = [row.model_dump(mode="json") for row in rows]
    jsonl_path = write_jsonl(data, output_dir / "data_quality_checks.jsonl")
    csv_path = write_csv(data, output_dir / "data_quality_checks.csv")
    summary = {
        "check_count": len(rows),
        "pass": sum(row.status == "pass" for row in rows),
        "warn": sum(row.status == "warn" for row in rows),
        "fail": sum(row.status == "fail" for row in rows),
        "missing": sum(row.status == "missing" for row in rows),
        "blocking_failures": sum(
            row.severity == "blocking" and row.status in {"fail", "missing"} for row in rows
        ),
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return jsonl_path, csv_path, summary_path


def _minimum_row_count_checks(repo: Path) -> list[DataQualityCheckRecord]:
    expectations = {
        "source_registry": (repo / "data" / "seed" / "source_registry.jsonl", 50),
        "analysis_catalogue": (repo / "data" / "seed" / "analysis_catalogue.jsonl", 20),
        "source_files": (repo / "data" / "seed" / "source_files.jsonl", 7),
        "conductor_tracks": (repo / "data" / "seed" / "conductor_tracks.jsonl", 8),
        "roadmap_functions": (repo / "data" / "seed" / "roadmap_functions.jsonl", 20),
        "dataset_candidates": (repo / "data" / "seed" / "dataset_candidates.jsonl", 15),
        "mapping_resources": (repo / "data" / "seed" / "mapping_resources.jsonl", 12),
        "research_questions": (repo / "data" / "seed" / "research_questions.jsonl", 5),
        "output_artifact_plans": (repo / "data" / "seed" / "output_artifact_plans.jsonl", 10),
        "vertical_schedule_items": (
            repo / "data" / "derived" / "vertical_slice" / "schedule_items.jsonl",
            10,
        ),
    }
    rows: list[DataQualityCheckRecord] = []
    for table_name, (path, minimum) in expectations.items():
        count = _jsonl_count(path)
        if count is None:
            rows.append(
                _check(
                    table_name,
                    "minimum_row_count",
                    "blocking",
                    "missing",
                    "missing",
                    f">={minimum}",
                    path,
                    "Regenerate required seed/derived artefacts.",
                )
            )
        else:
            rows.append(
                _check(
                    table_name,
                    "minimum_row_count",
                    "blocking",
                    "pass" if count >= minimum else "fail",
                    str(count),
                    f">={minimum}",
                    path,
                    "Add missing records or lower the expectation only through an ADR.",
                )
            )
    return rows


def _unique_id_checks(repo: Path) -> list[DataQualityCheckRecord]:
    paths = {
        "source_registry": repo / "data" / "seed" / "source_registry.jsonl",
        "analysis_catalogue": repo / "data" / "seed" / "analysis_catalogue.jsonl",
        "source_versions": repo / "data" / "seed" / "source_versions.jsonl",
        "source_files": repo / "data" / "seed" / "source_files.jsonl",
        "conductor_tracks": repo / "data" / "seed" / "conductor_tracks.jsonl",
        "roadmap_functions": repo / "data" / "seed" / "roadmap_functions.jsonl",
        "dataset_candidates": repo / "data" / "seed" / "dataset_candidates.jsonl",
        "mapping_resources": repo / "data" / "seed" / "mapping_resources.jsonl",
        "research_questions": repo / "data" / "seed" / "research_questions.jsonl",
        "output_artifact_plans": repo / "data" / "seed" / "output_artifact_plans.jsonl",
    }
    rows: list[DataQualityCheckRecord] = []
    for table_name, path in paths.items():
        records = _read_jsonl(path)
        if records is None:
            rows.append(
                _check(
                    table_name,
                    "unique_id",
                    "blocking",
                    "missing",
                    "missing",
                    "all ids unique",
                    path,
                    "Regenerate table before release.",
                )
            )
            continue
        ids = [str(row.get("id", "")) for row in records]
        duplicates = [item for item, count in Counter(ids).items() if item and count > 1]
        rows.append(
            _check(
                table_name,
                "unique_id",
                "blocking",
                "pass" if not duplicates and all(ids) else "fail",
                ";".join(duplicates) if duplicates else f"{len(ids)} ids",
                "all ids unique and non-empty",
                path,
                "Rename duplicate/empty identifiers and regenerate derived outputs.",
            )
        )
    return rows


def _referential_integrity_checks(repo: Path) -> list[DataQualityCheckRecord]:
    source_ids = _id_set(repo / "data" / "seed" / "source_registry.jsonl")
    version_ids = _id_set(repo / "data" / "seed" / "source_versions.jsonl")
    track_ids = _id_set(repo / "data" / "seed" / "conductor_tracks.jsonl")
    dataset_ids = source_ids | _id_set(repo / "data" / "seed" / "dataset_candidates.jsonl") | {"source_registry"}
    checks = [
        _foreign_key_check(
            repo,
            "source_files_source_id",
            repo / "data" / "seed" / "source_files.jsonl",
            "source_id",
            source_ids,
            "source_files.source_id references source_registry.id",
        ),
        _foreign_key_check(
            repo,
            "source_files_source_version_id",
            repo / "data" / "seed" / "source_files.jsonl",
            "source_version_id",
            version_ids,
            "source_files.source_version_id references source_versions.id",
        ),
        _foreign_key_check(
            repo,
            "roadmap_functions_track_id",
            repo / "data" / "seed" / "roadmap_functions.jsonl",
            "track_id",
            track_ids,
            "roadmap_functions.track_id references conductor_tracks.id",
        ),
        _foreign_key_check(
            repo,
            "research_questions_track_id",
            repo / "data" / "seed" / "research_questions.jsonl",
            "track_id",
            track_ids,
            "research_questions.track_id references conductor_tracks.id",
        ),
        _foreign_key_check(
            repo,
            "output_artifact_plans_track_id",
            repo / "data" / "seed" / "output_artifact_plans.jsonl",
            "track_id",
            track_ids,
            "output_artifact_plans.track_id references conductor_tracks.id",
        ),
        _tuple_foreign_key_check(
            repo,
            "research_questions_required_datasets",
            repo / "data" / "seed" / "research_questions.jsonl",
            "required_datasets",
            dataset_ids,
            "research question datasets resolve to sources or dataset candidates",
        ),
    ]
    return checks


def _generated_artifact_checks(repo: Path) -> list[DataQualityCheckRecord]:
    expectations = {
        "download_plans": repo / "data" / "derived" / "source_downloads" / "download_plans.jsonl",
        "source_content_validation": repo
        / "data"
        / "derived"
        / "source_validation"
        / "source_content_validation.jsonl",
        "protocol_status": repo / "data" / "derived" / "protocols" / "protocol_status.jsonl",
        "research_linkages": repo
        / "data"
        / "derived"
        / "roadmap_linkages"
        / "research_dataset_linkages.jsonl",
        "publication_manifest": repo / "data" / "derived" / "publication_manifest.json",
        "research_package_datapackage": repo / "data" / "derived" / "research_package" / "datapackage.json",
        "research_package_rocrate": repo / "data" / "derived" / "research_package" / "ro-crate-metadata.json",
    }
    rows: list[DataQualityCheckRecord] = []
    for table_name, path in expectations.items():
        exists = path.exists()
        rows.append(
            _check(
                table_name,
                "artifact_exists",
                "blocking",
                "pass" if exists else "missing",
                "present" if exists else "missing",
                "present",
                path,
                "Regenerate the artefact before release.",
            )
        )
    return rows


def _publication_safety_checks(repo: Path) -> list[DataQualityCheckRecord]:
    manifest_path = repo / "data" / "derived" / "publication_manifest.json"
    if not manifest_path.exists():
        return []
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    warnings = payload.get("warnings", [])
    raw_flags = 0
    for artifact in payload.get("artifacts", []):
        if isinstance(artifact, dict) and artifact.get("raw_source_payload"):
            raw_flags += 1
    return [
        _check(
            "publication_manifest",
            "raw_source_payload_absent",
            "blocking",
            "pass" if raw_flags == 0 else "fail",
            str(raw_flags),
            "0",
            manifest_path,
            "Remove raw/local/restricted artefacts from publication candidates.",
        ),
        _check(
            "publication_manifest",
            "warning_count_reviewed",
            "advisory",
            "pass" if not warnings else "warn",
            str(len(warnings)),
            "0 preferred",
            manifest_path,
            "Review warnings and document any accepted release caveats.",
        ),
    ]


def _foreign_key_check(
    repo: Path,
    check_id: str,
    path: Path,
    field: str,
    allowed: set[str],
    expected: str,
) -> DataQualityCheckRecord:
    records = _read_jsonl(path)
    if records is None:
        return _check(
            check_id,
            "foreign_key",
            "blocking",
            "missing",
            "missing table",
            expected,
            path,
            "Regenerate required seed table.",
        )
    missing = sorted({str(row.get(field, "")) for row in records if str(row.get(field, "")) not in allowed})
    return _check(
        check_id,
        "foreign_key",
        "blocking",
        "pass" if not missing else "fail",
        ";".join(missing) if missing else f"{len(records)} rows checked",
        expected,
        path,
        "Add missing parent records or correct child references.",
    )


def _tuple_foreign_key_check(
    repo: Path,
    check_id: str,
    path: Path,
    field: str,
    allowed: set[str],
    expected: str,
) -> DataQualityCheckRecord:
    records = _read_jsonl(path)
    if records is None:
        return _check(
            check_id,
            "foreign_key",
            "blocking",
            "missing",
            "missing table",
            expected,
            path,
            "Regenerate required seed table.",
        )
    seen: set[str] = set()
    for row in records:
        raw = row.get(field, [])
        values = raw if isinstance(raw, list) else [raw]
        seen.update(str(value) for value in values if str(value))
    missing = sorted(value for value in seen if value not in allowed)
    return _check(
        check_id,
        "foreign_key",
        "blocking",
        "pass" if not missing else "fail",
        ";".join(missing) if missing else f"{len(seen)} references checked",
        expected,
        path,
        "Add dataset/source candidate rows for every required research dataset.",
    )


def _read_jsonl(path: Path) -> list[dict[str, Any]] | None:
    if not path.exists():
        return None
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            loaded = json.loads(line)
            if isinstance(loaded, dict):
                records.append(loaded)
    return records


def _jsonl_count(path: Path) -> int | None:
    records = _read_jsonl(path)
    return None if records is None else len(records)


def _id_set(path: Path) -> set[str]:
    records = _read_jsonl(path) or []
    return {str(record.get("id")) for record in records if record.get("id")}


def _check(
    table_name: str,
    check_name: str,
    severity: str,
    status: str,
    observed_value: str,
    expected_value: str,
    path: Path,
    recommended_action: str,
) -> DataQualityCheckRecord:
    return DataQualityCheckRecord(
        id=_slug(f"{table_name}_{check_name}"),
        table_name=table_name,
        check_name=check_name,
        severity=severity,
        status=status,
        observed_value=observed_value,
        expected_value=expected_value,
        evidence_path=str(path),
        recommended_action=recommended_action,
    )


def _slug(value: str) -> str:
    safe = "".join(character.lower() if character.isalnum() else "_" for character in value)
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_") or "check"

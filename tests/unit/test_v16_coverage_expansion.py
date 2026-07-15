"""Additional branch coverage for v16 evidence-readiness helpers."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from reimburse_atlas import source_downloads
from reimburse_atlas.contracts import ScheduleItemRecord
from reimburse_atlas.data_quality import build_data_quality_checks, write_data_quality_checks
from reimburse_atlas.models import SourceFileRecord
from reimburse_atlas.roadmap_linkages import build_research_linkages
from reimburse_atlas.source_contracts import build_source_contract_validations
from reimburse_atlas.source_downloads import safe_local_target
from reimburse_atlas.source_validation import (
    build_source_content_validations,
    write_source_content_validations,
)
from reimburse_atlas.vector_index import (
    VectorIndexDependencyError,
    _create_or_replace_table,  # noqa: PLC2701
    build_lancedb_index,
    schedule_item_vector_rows,
    write_arrow_vector_seed,
)


def _source_file(record_id: str, *, expected_format: str = "TXT") -> SourceFileRecord:
    return SourceFileRecord(
        id=record_id,
        source_id="au_mbs",
        source_version_id="au_mbs_20260701_txt_pair",
        file_label="test source",
        file_name=f"{record_id}.TXT",
        source_url="https://example.test/source.txt",
        file_role="primary",
        expected_format=expected_format,
        acquisition_mode="manual_download",
        licence_gate="public_reuse_review",
        parser_hint="test parser",
        expected_record_count=2,
        current_observation="test",
        notes="test",
    )


def test_source_validation_detects_html_and_writes_outputs(tmp_path: Path) -> None:
    record = _source_file("html_error")
    target = safe_local_target(record, tmp_path)
    target.parent.mkdir(parents=True)
    target.write_text("<!doctype html><html>error</html>", encoding="utf-8")
    rows = build_source_content_validations([record], raw_dir=tmp_path)
    assert rows[0].validation_status == "fail"
    assert "HTML" in ";".join(rows[0].issues)
    paths = write_source_content_validations(rows, output_dir=tmp_path / "out")
    assert all(path.exists() for path in paths)
    assert json.loads(paths[2].read_text())["fail"] == 1


def test_source_validation_handles_json_and_zip_errors(tmp_path: Path) -> None:
    json_record = _source_file("json_bad", expected_format="json")
    json_target = safe_local_target(json_record, tmp_path).with_suffix(".json")
    # safe_local_target uses file_name, so align record filename with JSON target.
    json_record = json_record.model_copy(update={"file_name": json_target.name})
    json_target.parent.mkdir(parents=True, exist_ok=True)
    json_target.write_text("{not-json", encoding="utf-8")

    zip_record = _source_file("zip_bad", expected_format="ZIP containing CLFS file")
    zip_target = safe_local_target(zip_record, tmp_path).with_suffix(".zip")
    zip_record = zip_record.model_copy(update={"file_name": zip_target.name})
    zip_target.parent.mkdir(parents=True, exist_ok=True)
    zip_target.write_bytes(b"not a zip")

    rows = build_source_content_validations([json_record, zip_record], raw_dir=tmp_path)
    issues = " ".join(";".join(row.issues) for row in rows)
    assert "JSON parse failed" in issues
    assert "ZIP validation failed" in issues


def test_source_validation_uses_reviewed_bundle_when_raw_is_absent(tmp_path: Path) -> None:
    record = _source_file("au_mbs_20260701_imap_txt")
    bundle = tmp_path / "bundle_reviewed"
    bundle.mkdir()
    (bundle / "validation_report.json").write_text(
        json.dumps({
            "source_id": "au_mbs",
            "source_version_id": "au_mbs_20260701_txt_pair",
            "parse_success": True,
            "stats": {"item_map_rows": 2},
        }),
        encoding="utf-8",
    )
    (bundle / "source_snapshots.jsonl").write_text(
        json.dumps({
            "id": "snapshot_item_map",
            "byte_size": 32,
            "checksum_sha256": "a" * 64,
        })
        + "\n",
        encoding="utf-8",
    )

    rows = build_source_content_validations(
        [record], raw_dir=tmp_path / "raw", reviewed_bundle_dir=tmp_path
    )

    assert rows[0].validation_status == "pass"
    assert rows[0].byte_size == 32
    assert rows[0].observed_record_count == 2
    assert rows[0].local_target_ref == "reviewed_bundle:bundle_reviewed"


def test_source_validation_skips_api_documentation_even_when_downloaded(
    tmp_path: Path,
) -> None:
    record = _source_file("pbs_api_documentation").model_copy(
        update={
            "source_id": "au_pbs",
            "source_version_id": "au_pbs_api_v3_current_month",
            "file_role": "api_endpoint",
            "file_name": "PBS_API_CSV_endpoints.html",
            "expected_format": "JSON or CSV",
        }
    )
    target = safe_local_target(record, tmp_path)
    target.parent.mkdir(parents=True)
    target.write_text("<html>documentation</html>", encoding="utf-8")

    rows = build_source_content_validations([record], raw_dir=tmp_path)

    assert rows[0].validation_status == "skipped"
    assert "licence-gated" in rows[0].issues[0]


def test_source_contract_validation_uses_reviewed_bundle_when_raw_is_absent(
    tmp_path: Path,
) -> None:
    record = SourceFileRecord(
        id="au_mbs_20260701_imap_txt",
        source_id="au_mbs",
        source_version_id="au_mbs_20260701_txt_pair",
        file_label="MBS item map",
        file_name="item_map.TXT",
        source_url="https://example.test/mbs.txt",
        file_role="primary",
        expected_format="TXT",
        acquisition_mode="manual_download",
        licence_gate="public_reuse_review",
        parser_hint="parse_mbs_txt_pair item_map_path",
        expected_record_count=None,
        current_observation="reviewed bundle",
        notes="test",
    )
    bundle = tmp_path / "bundle_reviewed"
    bundle.mkdir()
    row = {
        "id": "contract_au_mbs_20260701_imap_txt",
        "source_file_id": record.id,
        "source_id": record.source_id,
        "source_version_id": record.source_version_id,
        "parser_hint": record.parser_hint,
        "contract_name": "MBS item-map TXT contract",
        "contract_status": "pass",
        "required_markers": ["item", "category"],
        "observed_markers": ["item", "category"],
        "expected_columns": ["item"],
        "observed_columns": ["item"],
        "byte_size": 32,
        "issues": [],
        "recommended_action": "Proceed.",
    }
    (bundle / "source_contract_validation.jsonl").write_text(
        json.dumps(row) + "\n", encoding="utf-8"
    )

    rows = build_source_contract_validations(
        [record], raw_dir=tmp_path / "raw", reviewed_bundle_dir=tmp_path
    )

    assert rows[0].contract_status == "pass"
    assert rows[0].byte_size == 32


def test_data_quality_missing_and_duplicate_paths(tmp_path: Path) -> None:
    seed = tmp_path / "data" / "seed"
    seed.mkdir(parents=True)
    # Minimal duplicate source registry; most other expected artefacts are intentionally missing.
    rows = [{"id": "x"}, {"id": "x"}]
    (seed / "source_registry.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )
    checks = build_data_quality_checks(tmp_path)
    assert any(check.status == "missing" for check in checks)
    assert any(check.check_name == "unique_id" and check.status == "fail" for check in checks)
    paths = write_data_quality_checks(checks, output_dir=tmp_path / "quality")
    assert all(path.exists() for path in paths)


def test_research_linkages_missing_and_dataset_candidate_paths() -> None:
    question = {
        "id": "rq_test",
        "track_id": "track_policy_demonstrators",
        "question": "Test medicines question",
        "protocol_path": "protocols/test.md",
        "report_path": "reports/test.md",
        "required_datasets": ["missing_dataset", "ds_test"],
        "methods": ["drug mapping"],
        "outputs": ["report"],
        "osf_component": "Test",
        "preregistration_status": "drafted",
    }
    from reimburse_atlas.models import (
        DatasetCandidateRecord,
        MappingResourceRecord,
        OutputArtifactPlanRecord,
        ResearchQuestionRecord,
    )

    rows = build_research_linkages(
        research_questions=[ResearchQuestionRecord.model_validate(question)],
        sources=[],
        dataset_candidates=[
            DatasetCandidateRecord(
                id="ds_test",
                jurisdiction="Testland",
                name="Test dataset",
                domain="medicine",
                source_url="https://example.test/dataset",
                access_mode="api",
                priority="must",
                licence_gate="public_reuse_review",
                parser_status="planned",
                recommended_next_step="Onboard.",
                notes="test",
            )
        ],
        mapping_resources=[
            MappingResourceRecord(
                id="rx_test",
                name="Rx test",
                domain="medicine",
                source_url="https://example.test/rx",
                access_mode="local_licence_only",
                licence_gate="restricted_or_licence_review",
                local_only=True,
                priority="must",
                mapping_strategy="drug mapping",
                notes="test",
            )
        ],
        output_plans=[
            OutputArtifactPlanRecord(
                id="out_test",
                track_id="track_policy_demonstrators",
                output_type="report",
                target_platform="osf",
                path="reports/test.md",
                status="planned",
                release_gate="protocol status",
                notes="test",
            )
        ],
    )
    assert any(row.readiness_status == "missing" for row in rows)
    assert any(row.readiness_status == "planned" for row in rows)
    assert any(row.readiness_status == "local_only" for row in rows)


def test_attempt_download_success_writes_metadata(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    record = _source_file("download_ok")

    def fake_run(args: list[str], **_: object) -> SimpleNamespace:
        target = Path(args[args.index("-o") + 1])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"item|group|fee\n1|A|12.30\n")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(source_downloads.subprocess, "run", fake_run)
    attempt = source_downloads.attempt_download(record, output_dir=tmp_path, timeout_seconds=1)
    plan = source_downloads.build_download_plan(record, output_dir=tmp_path)
    assert attempt.status == "downloaded"
    assert attempt.bytes_downloaded > 0
    assert Path(plan.metadata_path).exists()


def test_attempt_download_classifies_network_and_removes_empty_target(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    record = _source_file("download_network")

    def fake_run(args: list[str], **_: object) -> SimpleNamespace:
        target = Path(args[args.index("-o") + 1])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"")
        return SimpleNamespace(returncode=6, stdout="", stderr="Could not resolve host")

    monkeypatch.setattr(source_downloads.subprocess, "run", fake_run)
    attempt = source_downloads.attempt_download(record, output_dir=tmp_path, timeout_seconds=1)
    plan = source_downloads.build_download_plan(record, output_dir=tmp_path)
    assert attempt.status == "blocked_network"
    assert not Path(plan.target_path).exists()
    assert Path(plan.metadata_path).exists()


def test_attempt_download_uses_wget_and_skips_licence_gate(tmp_path: Path) -> None:
    record = _source_file("download_skip").model_copy(
        update={"licence_gate": "restricted_or_licence_review"}
    )
    plan = source_downloads.build_download_plan(
        record, output_dir=tmp_path, preferred_method="wget"
    )
    attempt = source_downloads.attempt_download(
        record, output_dir=tmp_path, preferred_method="wget"
    )
    assert plan.method == "wget"
    assert plan.should_execute is False
    assert attempt.method == "wget"
    assert attempt.status == "skipped_licence_gate"


def test_attempt_download_can_fallback_without_resume(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    record = _source_file("download_resume_fallback")
    calls: list[list[str]] = []

    def fake_run(args: list[str], **_: object) -> SimpleNamespace:
        calls.append(args)
        target = Path(args[args.index("-o") + 1])
        target.parent.mkdir(parents=True, exist_ok=True)
        if "--continue-at" in args or "--continue" in args:
            return SimpleNamespace(
                returncode=33, stdout="", stderr="server does not support byte ranges"
            )
        target.write_bytes(b"item|group|fee\n1|A|12.30\n")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(source_downloads.subprocess, "run", fake_run)
    attempt = source_downloads.attempt_download(
        record,
        output_dir=tmp_path,
        timeout_seconds=1,
        resume_downloads=True,
    )
    assert attempt.status == "downloaded"
    assert len(calls) == 2
    assert "--continue-at" in calls[0] or "--continue" in calls[0]
    assert "--continue-at" not in calls[1]
    assert "--continue" not in calls[1]


def test_source_validation_handles_non_file_valid_json_empty_zip_and_record_drift(
    tmp_path: Path,
) -> None:
    directory_record = _source_file("directory_target")
    directory_target = safe_local_target(directory_record, tmp_path)
    directory_target.mkdir(parents=True)

    json_record = _source_file("json_good", expected_format="json").model_copy(
        update={"file_name": "json_good.json", "expected_record_count": None}
    )
    json_target = safe_local_target(json_record, tmp_path)
    json_target.parent.mkdir(parents=True, exist_ok=True)
    json_target.write_text('{"ok": true}', encoding="utf-8")

    zip_record = _source_file("zip_empty", expected_format="ZIP containing CLFS file").model_copy(
        update={"file_name": "zip_empty.zip", "expected_record_count": None}
    )
    zip_target = safe_local_target(zip_record, tmp_path)
    with zipfile.ZipFile(zip_target, "w"):
        pass

    drift_record = _source_file("drift", expected_format="csv").model_copy(
        update={"file_name": "drift.csv", "expected_record_count": 100}
    )
    drift_target = safe_local_target(drift_record, tmp_path)
    drift_target.write_text("a,b\n1,2\n", encoding="utf-8")

    rows = build_source_content_validations(
        [directory_record, json_record, zip_record, drift_record],
        raw_dir=tmp_path,
    )
    by_id = {row.source_file_id: row for row in rows}
    assert by_id["directory_target"].validation_status == "fail"
    assert by_id["json_good"].validation_status == "pass"
    assert by_id["zip_empty"].validation_status == "warn"
    assert "record count" in ";".join(by_id["drift"].issues)


def test_vector_seed_rows_and_optional_dependency_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    record = ScheduleItemRecord(
        source_id="au_mbs",
        jurisdiction="Australia",
        domain="genomics",
        code_system="MBS",
        item_code="123",
        item_label="Genomic consultation",
        item_description="Complex genomic consultation and counselling",
        payment_amount=120.0,
        currency="AUD",
        payment_unit="item",
        patient_amount=None,
        restriction_text="once per patient",
        effective_from="2026-07-01",
        provenance={
            "source_id": "au_mbs",
            "source_version": "au_mbs_fixture",
            "licence_class": "public_reuse_unclear",
        },
    )
    rows = schedule_item_vector_rows([record], dimensions=8)
    assert rows[0]["item_code"] == "123"
    assert len(rows[0]["vector"]) == 8

    def missing_import(name: str) -> object:
        if name in {"pyarrow", "pyarrow.ipc", "lancedb"}:
            raise ModuleNotFoundError(name)
        raise AssertionError(name)

    monkeypatch.setattr("reimburse_atlas.vector_index.importlib.import_module", missing_import)
    with pytest.raises(VectorIndexDependencyError):
        write_arrow_vector_seed(rows, tmp_path / "vectors.arrow")
    with pytest.raises(VectorIndexDependencyError):
        build_lancedb_index(rows, database_dir=tmp_path / "lance")


def test_create_or_replace_table_drops_and_creates() -> None:
    class DummyDb:
        def __init__(self) -> None:
            self.actions: list[tuple[str, str, object]] = []

        def drop_table(self, table_name: str) -> None:
            self.actions.append(("drop", table_name, None))
            raise FileNotFoundError(table_name)

        def create_table(self, table_name: str, *, data: object) -> None:
            self.actions.append(("create", table_name, data))

    db = DummyDb()
    _create_or_replace_table(db, "items", [{"id": 1}])
    assert db.actions == [("drop", "items", None), ("create", "items", [{"id": 1}])]

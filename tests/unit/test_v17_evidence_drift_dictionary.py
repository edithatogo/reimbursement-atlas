from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from reimburse_atlas.data_dictionary import build_data_dictionary, write_data_dictionary
from reimburse_atlas.evidence_readiness import build_evidence_readiness, write_evidence_readiness
from reimburse_atlas.registry import project_root
from reimburse_atlas.source_drift import compare_tabular_files, write_source_drift_report


def test_evidence_readiness_marks_protocolled_questions_as_prototype_ready() -> None:
    rows = build_evidence_readiness()
    assert {row.readiness_stage for row in rows} == {"prototype_ready"}
    assert all(row.protocol_score > 0.8 for row in rows)
    assert all(row.data_quality_blockers == 0 for row in rows)


def test_evidence_readiness_writes_summary(tmp_path: Path) -> None:
    rows = build_evidence_readiness()
    _, _, summary_path = write_evidence_readiness(rows, output_dir=tmp_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["research_question_count"] == len(rows)
    assert summary["prototype_ready"] == len(rows)


def test_source_drift_detects_removed_columns(tmp_path: Path) -> None:
    left = tmp_path / "left.csv"
    right = tmp_path / "right.csv"
    left.write_text("id,name,price\n1,A,10\n", encoding="utf-8")
    right.write_text("id,name\n1,A\n", encoding="utf-8")
    row = compare_tabular_files(left, right, root=project_root())
    assert row.status == "fail"
    assert row.removed_columns == ("price",)


def test_source_drift_writes_report(tmp_path: Path) -> None:
    left = tmp_path / "left.jsonl"
    right = tmp_path / "right.jsonl"
    left.write_text('{"id":"a","value":1}\n', encoding="utf-8")
    right.write_text('{"id":"a","value":1}\n', encoding="utf-8")
    record = compare_tabular_files(left, right, left_label="left", right_label="right")
    _, _, summary_path = write_source_drift_report([record], output_dir=tmp_path / "drift")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["pass"] == 1
    assert summary["blocking_failure_count"] == 0


def test_data_dictionary_includes_publication_candidates(tmp_path: Path) -> None:
    rows = build_data_dictionary()
    assert any(row.relative_path.endswith("source_registry.csv") for row in rows)
    assert all("raw_live" not in row.relative_path for row in rows)
    _, csv_path, summary_path = write_data_dictionary(rows, output_dir=tmp_path)
    assert csv_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["table_count"] == len(rows)
    assert summary["total_rows_documented"] >= 0


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_evidence_readiness_covers_blocked_design_and_ready_paths(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path / "data/seed/research_questions.jsonl",
        [
            {"id": "ready", "track_id": "track"},
            {"id": "design", "track_id": "track"},
        ],
    )
    _write_jsonl(
        tmp_path / "data/derived/protocols/protocol_status.jsonl",
        [
            {"research_question_id": "ready", "completeness_score": 0.95},
            {"research_question_id": "design", "completeness_score": 0.2},
        ],
    )
    _write_jsonl(
        tmp_path / "data/derived/roadmap_linkages/research_dataset_linkages.jsonl",
        [
            {
                "research_question_id": "ready",
                "readiness_status": "available",
                "linked_entity_type": "source",
            },
            {
                "research_question_id": "ready",
                "readiness_status": "available",
                "linked_entity_type": "dataset_candidate",
            },
            {
                "research_question_id": "ready",
                "readiness_status": "available",
                "linked_entity_type": "mapping_resource",
            },
            {
                "research_question_id": "ready",
                "readiness_status": "available",
                "linked_entity_type": "source",
            },
            {
                "research_question_id": "ready",
                "readiness_status": "available",
                "linked_entity_type": "dataset_candidate",
            },
            {
                "research_question_id": "ready",
                "readiness_status": "available",
                "linked_entity_type": "mapping_resource",
            },
            {
                "research_question_id": "ready",
                "readiness_status": "available",
                "linked_entity_type": "output",
            },
            {
                "research_question_id": "ready",
                "readiness_status": "available",
                "linked_entity_type": "output",
            },
            {
                "research_question_id": "design",
                "readiness_status": "missing",
                "linked_entity_type": "source",
            },
        ],
    )
    _write_jsonl(tmp_path / "data/derived/data_quality/data_quality_checks.jsonl", [])
    _write_jsonl(
        tmp_path / "data/derived/source_validation/source_content_validation.jsonl",
        [],
    )

    rows = {row.research_question_id: row for row in build_evidence_readiness(tmp_path)}
    assert rows["ready"].readiness_stage == "prototype_ready"
    assert rows["ready"].claim_package_status == "missing"
    assert "checksum-bound claim package" in rows["ready"].recommended_action
    assert rows["design"].readiness_stage == "design"
    assert "Expand the OSF protocol" in rows["design"].recommended_action

    _write_jsonl(
        tmp_path / "data/derived/data_quality/data_quality_checks.jsonl",
        [{"severity": "blocking", "status": "fail"}],
    )
    blocked = {row.research_question_id: row for row in build_evidence_readiness(tmp_path)}
    assert blocked["ready"].readiness_stage == "blocked"
    assert "data-quality" in blocked["ready"].recommended_action


def test_evidence_readiness_requires_valid_approved_claim_package(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path / "data/seed/research_questions.jsonl",
        [{"id": "ready", "track_id": "track"}],
    )
    _write_jsonl(
        tmp_path / "data/derived/protocols/protocol_status.jsonl",
        [{"research_question_id": "ready", "completeness_score": 0.95}],
    )
    _write_jsonl(
        tmp_path / "data/derived/roadmap_linkages/research_dataset_linkages.jsonl",
        [
            {
                "research_question_id": "ready",
                "readiness_status": "available",
                "linked_entity_type": entity_type,
            }
            for entity_type in (
                "source",
                "source",
                "dataset_candidate",
                "dataset_candidate",
                "mapping_resource",
                "mapping_resource",
                "output",
                "output",
            )
        ],
    )
    _write_jsonl(tmp_path / "data/derived/data_quality/data_quality_checks.jsonl", [])
    _write_jsonl(tmp_path / "data/derived/source_validation/source_content_validation.jsonl", [])
    package = tmp_path / "data/derived/research_claims/ready.json"
    package.parent.mkdir(parents=True)
    package.write_text(
        json.dumps({
            "research_question_id": "ready",
            "analysis_status": "complete",
            "missing_reviewed_sources": [],
            "validation": {
                "deterministic": True,
                "reviewed_inputs_only": True,
                "raw_payloads_included": False,
                "restricted_descriptors_included": False,
                "analysis_validated": True,
            },
        })
        + "\n",
        encoding="utf-8",
    )
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    _write_jsonl(
        tmp_path / "data/research_claims/decisions.jsonl",
        [
            {
                "research_question_id": "ready",
                "claim_package_path": "data/derived/research_claims/ready.json",
                "claim_package_sha256": digest,
                "status": "approved_within_scope",
                "reviewed_derived_inputs": True,
                "analysis_validated": True,
                "review_record": "owner-review-1",
            }
        ],
    )

    row = build_evidence_readiness(tmp_path)[0]
    assert row.readiness_stage == "evidence_ready"
    assert row.claim_package_status == "approved"

    package.write_text('{"analysis_status":"partial"}\n', encoding="utf-8")
    stale = build_evidence_readiness(tmp_path)[0]
    assert stale.readiness_stage == "prototype_ready"
    assert stale.claim_package_status == "invalid"


def test_evidence_readiness_source_blocker_and_empty_summary(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path / "data/seed/research_questions.jsonl",
        [{"id": "blocked", "track_id": "track"}],
    )
    _write_jsonl(
        tmp_path / "data/derived/protocols/protocol_status.jsonl",
        [{"research_question_id": "blocked", "completeness_score": 0.8}],
    )
    _write_jsonl(
        tmp_path / "data/derived/roadmap_linkages/research_dataset_linkages.jsonl",
        [
            {
                "research_question_id": "blocked",
                "readiness_status": "blocked",
                "linked_entity_type": "dataset_candidate",
            }
        ],
    )
    _write_jsonl(tmp_path / "data/derived/data_quality/data_quality_checks.jsonl", [])
    _write_jsonl(
        tmp_path / "data/derived/source_validation/source_content_validation.jsonl",
        [{"validation_status": "fail"}],
    )

    row = build_evidence_readiness(tmp_path)[0]
    assert row.readiness_stage == "blocked"
    assert "source-content validation" in row.recommended_action

    _, _, summary_path = write_evidence_readiness([], output_dir=tmp_path / "empty")
    assert json.loads(summary_path.read_text(encoding="utf-8"))["average_readiness_score"] == 0.0


def test_source_drift_missing_added_columns_row_counts_and_text_files(tmp_path: Path) -> None:
    missing = compare_tabular_files(tmp_path / "missing-left.csv", tmp_path / "missing-right.csv")
    assert missing.status == "missing"
    assert "Generate missing" in missing.recommended_action

    left = tmp_path / "left.csv"
    right = tmp_path / "right.csv"
    left.write_text("id\n1\n", encoding="utf-8")
    right.write_text("id,extra\n1,x\n", encoding="utf-8")
    added = compare_tabular_files(left, right, root=tmp_path / "elsewhere")
    assert added.status == "warn"
    assert added.added_columns == ("extra",)
    assert added.left_path.startswith(str(tmp_path))

    longer = tmp_path / "longer.csv"
    longer.write_text("id\n1\n2\n", encoding="utf-8")
    count_drift = compare_tabular_files(left, longer, root=tmp_path)
    assert count_drift.status == "warn"
    assert "row-count drift" in count_drift.recommended_action

    text_left = tmp_path / "left.txt"
    text_right = tmp_path / "right.txt"
    text_left.write_text("a\nb\n", encoding="utf-8")
    text_right.write_text("a\nb\n", encoding="utf-8")
    text_record = compare_tabular_files(text_left, text_right, root=tmp_path)
    assert text_record.status == "pass"
    assert text_record.left_row_count == 2


def test_data_dictionary_handles_json_metadata_and_invalid_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import reimburse_atlas.data_dictionary as dictionary_module

    (tmp_path / "metadata.json").write_text('{"name":"atlas","version":"1"}\n', encoding="utf-8")
    (tmp_path / "bad.json").write_text("{not-json", encoding="utf-8")
    (tmp_path / "seed.csv").write_text("id,value\na,1\n", encoding="utf-8")
    (tmp_path / "raw_live").mkdir()
    (tmp_path / "raw_live/foo.csv").write_text("id\nsecret\n", encoding="utf-8")
    monkeypatch.setattr(
        dictionary_module,
        "DEFAULT_PUBLICATION_PATHS",
        (
            Path("metadata.json"),
            Path("bad.json"),
            Path("seed.csv"),
            Path("raw_live/foo.csv"),
        ),
    )

    rows = build_data_dictionary(root=tmp_path)
    by_path = {row.relative_path: row for row in rows}
    assert by_path["metadata.json"].columns == ("name", "version")
    assert by_path["bad.json"].columns == ()
    assert by_path["seed.csv"].publication_scope == "public_metadata_candidate"
    assert "raw_live/foo.csv" not in by_path

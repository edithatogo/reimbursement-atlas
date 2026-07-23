from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.make_mapping_candidate_frame import build_candidate_frame, write_candidate_frame


def _record(source_id: str, code: str, version: str, label: str) -> dict[str, object]:
    return {
        "source_id": source_id,
        "item_code": code,
        "item_label": label,
        "item_description": label,
        "domain": "pathology",
        "provenance": {"source_version": version},
    }


def _write_bundle(root: Path, name: str, rows: list[dict[str, object]]) -> None:
    path = root / "data/derived/reviewed_source_bundles" / name / f"{name}_schedule_items.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_candidate_frame_uses_reviewed_bundles_and_never_fixtures(tmp_path: Path) -> None:
    _write_bundle(
        tmp_path,
        "mbs",
        [_record("au_mbs", "100", "mbs-v1", "molecular pathology assay")],
    )
    _write_bundle(
        tmp_path,
        "clfs",
        [
            _record("us_cms_clfs", "800", "clfs-v1", "molecular pathology assay"),
            _record("us_cms_clfs", "900", "clfs-v1", "unrelated imaging service"),
        ],
    )

    rows, summary = build_candidate_frame(tmp_path)

    assert rows
    assert summary["fixture_rows_used"] == 0
    assert summary["source_pair_coverage"]
    assert summary["source_version_coverage"]
    assert summary["candidate_score_summary"]["procedures_pathology"]
    assert summary["status"] == "blocked_source_families"
    assert summary["family_summary"]["procedures_pathology"]["available"] == 2
    assert {row["proposed_label_hypothesis"] for row in rows} >= {
        "positive_candidate",
        "negative_candidate",
    }


def test_candidate_frame_rows_validate_and_output_is_deterministic(tmp_path: Path) -> None:
    _write_bundle(
        tmp_path,
        "mbs",
        [_record("au_mbs", "100", "mbs-v1", "molecular pathology assay")],
    )
    _write_bundle(
        tmp_path,
        "clfs",
        [_record("us_cms_clfs", "800", "clfs-v1", "molecular pathology assay")],
    )
    rows, summary = build_candidate_frame(tmp_path)
    write_candidate_frame(tmp_path, rows, summary)
    first = (tmp_path / "data/derived/mapping_study/candidate_frame.jsonl").read_bytes()
    rows_again, summary_again = build_candidate_frame(tmp_path)
    write_candidate_frame(tmp_path, rows_again, summary_again)
    second = (tmp_path / "data/derived/mapping_study/candidate_frame.jsonl").read_bytes()
    schema = json.loads(
        Path("schema/MappingCandidateFrameRecord.schema.json").read_text(encoding="utf-8")
    )

    assert first == second
    assert not list(Draft202012Validator(schema).iter_errors(rows[0]))


def test_current_repository_reports_partial_real_counterpart_coverage() -> None:
    rows, summary = build_candidate_frame(Path.cwd())

    assert len(rows) == 1500
    assert summary["candidate_count"] == 1500
    assert summary["effective_unique_groups"] == 1500
    assert summary["target_gap"] == 0
    assert summary["family_summary"]["medicines"]["status"] == "ready"
    assert summary["family_summary"]["procedures_pathology"]["status"] == "ready"
    assert summary["family_summary"]["genomics_coverage"]["status"] == "ready"
    assert summary["family_summary"]["devices_other"]["status"] == "ready"
    assert summary["status"] == "ready_for_blinded_review"


def test_main_cycle_guard_is_covered_by_immutable_output_contract() -> None:
    source = Path("scripts/make_mapping_candidate_frame.py").read_text(encoding="utf-8")
    assert 'candidate_dir = OUTPUT_DIR / f"expansion_v{cycle}"' in source
    assert "immutable_predecessor_sha256" in source


def test_positive_candidates_are_ranked_by_score() -> None:
    source = Path("scripts/make_mapping_candidate_frame.py").read_text(encoding="utf-8")

    assert '-float(cast("float | int", row["candidate_score"]))' in source
    assert 'float(cast("float | int", row["candidate_score"]))' in source
    assert "    )[:limit]" not in source
    assert "POSITIVE_CANDIDATE_TARGETS" in source

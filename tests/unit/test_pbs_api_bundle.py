"""Tests for derived-only reviewed PBS API bundles."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from reimburse_atlas.local_sources import build_pbs_api_bundle


def _write_inputs(tmp_path: Path) -> tuple[list[Path], Path]:
    schedules = tmp_path / "schedules.json"
    schedules.write_text(
        '{"data": [{"schedule_code": 4706, "effective_date": "2026-07-01"}]}\n',
        encoding="utf-8",
    )
    page_one = tmp_path / "items_page_1.csv"
    page_one.write_text(
        "pbs_code,drug_name,li_form,determined_price,schedule_code\n"
        "10001J,Rifaximin,Tablet 550 mg,394.14,4706\n"
        "10002K,Medicine B,Capsule,12.50,4706\n",
        encoding="utf-8",
    )
    page_two = tmp_path / "items_page_2.csv"
    page_two.write_text(
        "pbs_code,drug_name,li_form,determined_price,schedule_code\n"
        "10002K,Medicine B duplicate,Capsule,12.50,4706\n"
        "10003L,Medicine C,Injection,50.00,4706\n",
        encoding="utf-8",
    )
    return [page_two, page_one], schedules


def test_build_pbs_api_bundle_is_derived_only_and_deterministic(tmp_path: Path) -> None:
    """All pages are joined, code-deduplicated and provenance-bound."""
    item_paths, schedules = _write_inputs(tmp_path)
    first = build_pbs_api_bundle(
        item_paths=item_paths,
        schedules_path=schedules,
        output_dir=tmp_path / "first",
        retrieved_at="2026-07-18T00:00:00+00:00",
    )
    second = build_pbs_api_bundle(
        item_paths=list(reversed(item_paths)),
        schedules_path=schedules,
        output_dir=tmp_path / "second",
        retrieved_at="2026-07-18T00:00:00+00:00",
    )

    assert first.bundle_id == second.bundle_id
    assert first.input_record_count == 4
    assert first.record_count == 3
    assert first.duplicate_item_count == 1
    assert first.parsed_jsonl_path.read_bytes() == second.parsed_jsonl_path.read_bytes()

    snapshots = first.snapshot_jsonl_path.read_text(encoding="utf-8")
    assert str(tmp_path) not in snapshots
    assert '"local_path": null' in snapshots
    rows = [json.loads(line) for line in first.parsed_jsonl_path.read_text().splitlines()]
    assert {row["provenance"]["source_version"] for row in rows} == {"au_pbs_api_v3_current_month"}
    report = json.loads(first.validation_report_path.read_text(encoding="utf-8"))
    assert report["input_page_count"] == 2
    assert report["deduplication_key"] == "item_code"
    assert report["raw_files_copied_to_bundle"] is False


def test_build_pbs_api_bundle_requires_an_items_page(tmp_path: Path) -> None:
    schedules = tmp_path / "schedules.json"
    schedules.write_text('{"data": []}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="at least one PBS items page"):
        build_pbs_api_bundle(
            item_paths=[],
            schedules_path=schedules,
            output_dir=tmp_path / "bundle",
        )

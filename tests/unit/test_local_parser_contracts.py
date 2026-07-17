"""Tests for local source parser-contract validation."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.check_local_parser_contracts import build_report


def test_local_parser_contracts_skip_without_ignored_caches(tmp_path: Path) -> None:
    """Absent local caches produce an honest non-blocking skipped report."""
    report = build_report(tmp_path)

    assert report["status"] == "skipped"
    assert report["network_io"] is False
    assert report["mutation_performed"] is False
    assert all(source["status"] == "skipped" for source in report["sources"].values())


def test_pbs_contract_preserves_duplicate_item_codes(tmp_path: Path) -> None:
    """Repeated PBS codes are reported, not rejected as malformed input."""
    cache = tmp_path / "data/raw_live/au_pbs"
    cache.mkdir(parents=True)
    (cache / "pbs_v3_items_4706.csv").write_text(
        "li_item_id,drug_name,schedule_code\n100,Alpha,4706\n100,Alpha brand,4706\n",
        encoding="utf-8",
    )
    (cache / "pbs_v3_schedules.json").write_text(
        json.dumps({"data": [{"schedule_code": "4706", "effective_date": "2026-07-01"}]}),
        encoding="utf-8",
    )
    (cache / "pbs_v3_fees_4706.csv").write_text(
        "schedule_code,fee\n4706,1.00\n",
        encoding="utf-8",
    )

    report = build_report(tmp_path)
    pbs = report["sources"]["au_pbs_api_csv"]

    assert report["status"] == "pass"
    assert pbs["checks"]["item_codes_present"] is True
    assert pbs["counts"]["duplicate_item_codes"] == 1

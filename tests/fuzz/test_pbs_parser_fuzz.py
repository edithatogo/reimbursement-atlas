"""Bounded structure-aware fuzzing for PBS parser trust boundaries."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from reimburse_atlas.parsers.pbs_csv import parse_pbs_api_csv, parse_pbs_csv

FUZZ_SETTINGS = settings(
    max_examples=400, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture]
)
SAFE_TEXT = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",), blacklist_characters="\x00"), max_size=80
)


@FUZZ_SETTINGS
@given(
    code=SAFE_TEXT, label=SAFE_TEXT, amount=SAFE_TEXT, effective=SAFE_TEXT, restriction=SAFE_TEXT
)
def test_pbs_csv_untrusted_cells(
    tmp_path: Path, code: str, label: str, amount: str, effective: str, restriction: str
) -> None:
    path = tmp_path / "fuzz.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["pbs_item_code", "drug_name", "price", "effective_date", "restriction"],
        )
        writer.writeheader()
        writer.writerow({
            "pbs_item_code": code,
            "drug_name": label,
            "price": amount,
            "effective_date": effective,
            "restriction": restriction,
        })
    records = parse_pbs_csv(path)
    assert len(records) <= 1
    assert all(record.provenance.source_id == "au_pbs" for record in records)
    assert all(str(tmp_path) not in record.provenance.transformation_notes for record in records)


@FUZZ_SETTINGS
@given(
    payload=st.recursive(
        st.none() | st.booleans() | st.integers() | SAFE_TEXT,
        lambda x: st.lists(x, max_size=5) | st.dictionaries(SAFE_TEXT, x, max_size=5),
        max_leaves=20,
    )
)
def test_pbs_schedule_json_shapes(tmp_path: Path, payload: object) -> None:
    items = tmp_path / "items.csv"
    items.write_text("pbs_item_code,schedule_code\n1,S1\n", encoding="utf-8")
    schedules = tmp_path / "schedules.json"
    schedules.write_text(json.dumps(payload), encoding="utf-8")
    try:
        records = parse_pbs_api_csv(items, schedules)
    except TypeError, ValueError:
        return
    assert len(records) == 1

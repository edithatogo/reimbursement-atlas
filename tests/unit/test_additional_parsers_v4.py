"""Tests for v4 parser expansions."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.models import SourceFileRecord
from reimburse_atlas.parsers import (
    parse_cms_asp_csv,
    parse_cms_pfs_csv,
    parse_pbs_api_csv,
    parse_pbs_csv,
)
from reimburse_atlas.pbs_api_evidence import build_pbs_api_evidence, write_pbs_api_evidence
from reimburse_atlas.source_contracts import validate_path_against_contract


def test_parse_pbs_fixture(repo_root: Path) -> None:
    """PBS parser should preserve medicines pricing caveats in provenance."""
    records = parse_pbs_csv(repo_root / "tests" / "fixtures" / "pbs_fixture.csv")
    assert len(records) == 2
    assert records[0].source_id == "au_pbs"
    assert records[0].currency == "AUD"
    assert records[0].payment_unit == "pack"
    assert records[0].patient_amount == 31.6
    assert "net effective price" in (records[0].provenance.transformation_notes or "")


def test_parse_cms_asp_fixture(repo_root: Path) -> None:
    """CMS ASP parser should emit Part B medicine schedule rows."""
    records = parse_cms_asp_csv(repo_root / "tests" / "fixtures" / "cms_asp_fixture.csv")
    assert len(records) == 2
    assert records[0].source_id == "us_cms_asp"
    assert records[0].code_system == "HCPCS_ASP"
    assert records[0].payment_amount == 87.65
    assert records[0].setting == "part_b"


def test_parse_live_pbs_items_with_schedule_join(tmp_path: Path) -> None:
    items = tmp_path / "items.csv"
    items.write_text(
        "pbs_code,drug_name,li_form,determined_price,schedule_code,legal_car_ind\n"
        "10001J,Rifaximin,Tablet 550 mg,394.14,4706,Y\n",
        encoding="utf-8",
    )
    schedules = tmp_path / "schedules.json"
    schedules.write_text(
        '{"data": [{"schedule_code": 4706, "effective_date": "2026-07-01"}]}\n',
        encoding="utf-8",
    )

    records = parse_pbs_api_csv(items, schedules)

    assert len(records) == 1
    assert records[0].item_code == "10001J"
    assert records[0].payment_amount == 394.14
    assert str(records[0].effective_from) == "2026-07-01"
    assert records[0].provenance.source_version == "au_pbs_api_v3_current_month"


def test_live_pbs_items_shape_matches_contract(tmp_path: Path) -> None:
    items = tmp_path / "items.csv"
    items.write_text(
        "pbs_code,drug_name,schedule_code\n10001J,Rifaximin,4706\n",
        encoding="utf-8",
    )
    record = SourceFileRecord.model_validate({
        "id": "au_pbs_api_v3_documentation",
        "source_id": "au_pbs",
        "source_version_id": "au_pbs_api_v3_current_month",
        "file_label": "PBS API items",
        "file_name": "items.csv",
        "source_url": "https://data-api.health.gov.au/pbs/api/v3/items",
        "file_role": "api_endpoint",
        "expected_format": "CSV",
        "acquisition_mode": "api_rate_limited",
        "licence_gate": "public_reuse_review",
        "parser_hint": "parse PBS API items",
        "current_observation": "live API shape",
        "notes": "fixture",
    })

    result = validate_path_against_contract(record, items)

    assert result.contract_status == "pass"


def test_build_pbs_api_evidence_redacts_local_paths_and_checks_schema(tmp_path: Path) -> None:
    schedules = tmp_path / "schedules.json"
    schedules.write_text(
        '{"data": [{"schedule_code": 4706, "effective_date": "2026-07-01"}]}\n',
        encoding="utf-8",
    )
    items = tmp_path / "items-page-1.csv"
    items.write_text(
        "pbs_code,drug_name,schedule_code\n10001J,Rifaximin,4706\n",
        encoding="utf-8",
    )
    fees = tmp_path / "fees.csv"
    fees.write_text("schedule_code,fee_type\n4706,dispensing\n", encoding="utf-8")

    rows = build_pbs_api_evidence(
        schedules,
        (items,),
        fees,
        schedule_code="4706",
        retrieved_at="2026-07-16",
    )
    assert [row.endpoint for row in rows] == ["schedules", "items", "fees"]
    assert all(row.schema_status == "pass" for row in rows)
    assert all(str(tmp_path) not in (row.local_target_ref or "") for row in rows)
    assert rows[1].record_count == 1

    paths = write_pbs_api_evidence(rows, output_dir=tmp_path / "output")
    assert all(path.exists() for path in paths)
    assert '"raw_payloads_tracked": false' in paths[2].read_text(encoding="utf-8")


def test_parse_cms_pfs_fixture(repo_root: Path) -> None:
    """CMS PFS parser should prefer non-facility payment amounts."""
    records = parse_cms_pfs_csv(repo_root / "tests" / "fixtures" / "cms_pfs_fixture.csv")
    assert len(records) == 2
    assert records[1].source_id == "us_cms_pfs"
    assert records[1].item_code == "96040"
    assert records[1].payment_amount == 74.6
    assert records[1].professional_component is True

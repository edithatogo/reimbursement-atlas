"""Contracts for newly promoted public machine-readable source adapters."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import polars as pl
import pytest

from reimburse_atlas.parsers.cms_mcd_ncd_csv import parse_cms_mcd_ncd_csv
from reimburse_atlas.parsers.nhs_genomic_directory_xlsx import (
    parse_nhs_genomic_directory_xlsx,
)
from reimburse_atlas.parsers.nhs_payment_scheme_xlsx import parse_nhs_payment_scheme_xlsx
from reimburse_atlas.parsers.ohip_master_text import parse_ohip_master_text
from reimburse_atlas.parsers.pharmac_xml import parse_pharmac_xml


def test_nhs_genomic_workbook_uses_real_excel_reader(tmp_path: Path) -> None:
    """Exercise Polars and fastexcel together using a synthetic OOXML workbook."""
    source = tmp_path / "genomic.xlsx"
    with ZipFile(source, "w") as workbook:
        workbook.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" '
            'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>",
        )
        for filename, target, relation in (
            ("_rels/.rels", "xl/workbook.xml", "officeDocument"),
            ("xl/_rels/workbook.xml.rels", "worksheets/sheet1.xml", "worksheet"),
        ):
            workbook.writestr(
                filename,
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f'<Relationship Id="rId1" Target="{target}" '
                f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/{relation}"/>'
                "</Relationships>",
            )
        workbook.writestr(
            "xl/workbook.xml",
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="R&amp;ID indications" sheetId="1" r:id="rId1"/></sheets>'
            "</workbook>",
        )
        workbook.writestr(
            "xl/worksheets/sheet1.xml",
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData><row r="1">'
            '<c r="A1" t="inlineStr"><is><t>Clinical indication ID</t></is></c>'
            '<c r="B1" t="inlineStr"><is><t>Test ID</t></is></c>'
            '<c r="C1" t="inlineStr"><is><t>Clinical Indication</t></is></c>'
            '</row><row r="2">'
            '<c r="A2" t="inlineStr"><is><t>R1</t></is></c>'
            '<c r="B2" t="inlineStr"><is><t>R1.1</t></is></c>'
            '<c r="C2" t="inlineStr"><is><t>Synthetic indication</t></is></c>'
            "</row></sheetData></worksheet>",
        )
    records = parse_nhs_genomic_directory_xlsx(source)
    assert len(records) == 1
    assert records[0].decision_id == "R1.1"
    assert records[0].technology_name == "Synthetic indication"
    assert records[0].decision_status == "covered_with_restrictions"


def test_pharmac_xml_parses_public_subsidy(tmp_path: Path) -> None:
    source = tmp_path / "schedule.xml"
    source.write_text(
        """<?xml version="1.0"?>
<Schedule xmlns="http://schedule.pharmac.govt.nz/2006/07/Schedule#">
  <Section><Chemical ID="C1"><Name>Medicine</Name>
    <Formulation ID="F1"><Name>tablet</Name><Brand ID="B1"><Name>Brand</Name>
      <Pack ID="P1"><Quantity>30</Quantity><Subsidy>12.34</Subsidy></Pack>
    </Brand></Formulation>
  </Chemical></Section>
</Schedule>""",
        encoding="utf-8",
    )
    rows = parse_pharmac_xml(source)
    assert len(rows) == 1
    assert rows[0].payment_amount == 12.34
    assert rows[0].item_code == "P1"


def test_nhs_genomic_xlsx_requires_and_parses_schema(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "genomic.xlsx"
    frame = pl.DataFrame({
        "Clinical indication ID": ["R1"],
        "Test ID": ["R1.1"],
        "Clinical Indication": ["Condition"],
        "Test Method": ["WGS"],
        "Commissioning category": ["Core"],
    })

    def fake_read_excel(*_args: object, **_kwargs: object) -> pl.DataFrame:
        return frame

    monkeypatch.setattr(pl, "read_excel", fake_read_excel)
    rows = parse_nhs_genomic_directory_xlsx(source)
    assert len(rows) == 1
    assert rows[0].decision_status == "covered_with_restrictions"


def test_nhs_payment_xlsx_parses_only_numeric_prices(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "payment.xlsx"
    frame = pl.DataFrame({
        "TMC": ["TMC1"],
        "Test Method": ["METHOD"],
        "Cancer / Rare Disease Test Price (£)": [100],
        "Cancer Report Price (£)": [None],
        "Rare Disease Report Price (£)": [50],
    })

    def fake_read_excel(*_args: object, **_kwargs: object) -> pl.DataFrame:
        return frame

    monkeypatch.setattr(pl, "read_excel", fake_read_excel)
    rows = parse_nhs_payment_scheme_xlsx(source)
    assert [row.payment_amount for row in rows] == [100.0, 50.0]


def test_ohip_fixed_width_parses_first_positive_fee(tmp_path: Path) -> None:
    source = tmp_path / "ohip.001"
    source.write_text("A00120260401999999990000026800000000\n", encoding="ascii")
    rows = parse_ohip_master_text(source)
    assert len(rows) == 1
    assert rows[0].payment_amount == 2.68


def test_cms_mcd_excludes_document_body(tmp_path: Path) -> None:
    source = tmp_path / "ncd.csv"
    source.write_text(
        "NCD_id,NCD_vrsn_num,NCD_mnl_sect_title,natl_cvrg_type,"
        "NCD_trmntn_dt,NCD_efctv_dt,indctn_lmtn\n"
        "1,2,Example NCD,True,,2026-01-01 00:00:00,restricted body\n",
        encoding="utf-8",
    )
    rows = parse_cms_mcd_ncd_csv(source)
    assert len(rows) == 1
    assert rows[0].decision_status == "covered"
    assert "restricted body" not in rows[0].model_dump_json()

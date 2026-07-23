from __future__ import annotations

from pathlib import Path

from reimburse_atlas.parsers.cms_asp_csv import parse_cms_asp_csv


def test_official_section_508_csv_preamble_and_provenance(tmp_path: Path) -> None:
    source = tmp_path / "asp.csv"
    source.write_text(
        "Payment Allowance Limits for Medicare Part B Drugs,,,,\n"
        "Effective July 1, 2026 through September 30, 2026,,,,\n"
        "HCPCS Code,Short Description,HCPCS Code Dosage,Payment Limit,Notes\n"
        "J0123,Example drug,1 MG,12.345,Public payment limit\n",
        encoding="utf-8",
    )

    records = parse_cms_asp_csv(
        source,
        source_version="us_cms_asp_july_2026_payment_limit",
        retrieved_at="2026-06-17T00:00:00Z",
    )

    assert len(records) == 1
    assert records[0].item_code == "J0123"
    assert records[0].payment_amount == 12.345
    assert records[0].payment_unit == "1 MG"
    assert records[0].provenance.source_version == "us_cms_asp_july_2026_payment_limit"
    assert "not coverage" in str(records[0].provenance.transformation_notes)


def test_official_section_508_csv_accepts_cp1252(tmp_path: Path) -> None:
    source = tmp_path / "asp.csv"
    source.write_bytes(
        "HCPCS Code,Short Description,HCPCS Code Dosage,Payment Limit,Notes\n"
        "J0123,Example drug,1 MG,12.345,manufacturer\u00a0note\n".encode("cp1252")
    )

    records = parse_cms_asp_csv(source)

    assert records[0].item_code == "J0123"

"""Tests for first-wave public schedule parser prototypes."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.parsers import (
    parse_cms_clfs_csv,
    parse_mbs_xml,
    parse_nhs_genomic_directory_csv,
)


def test_parse_mbs_xml_fragment(repo_root: Path) -> None:
    """MBS parser should emit schedule item contracts from XML-like fixtures."""
    records = parse_mbs_xml(repo_root / "tests" / "fixtures" / "mbs_fragment.xml")
    assert len(records) == 2
    assert records[0].source_id == "au_mbs"
    assert records[0].currency == "AUD"
    assert records[0].payment_amount == 1200.0
    assert records[0].provenance.licence_class == "public_reuse_unclear"


def test_parse_mbs_xml_data_release_shape(tmp_path: Path) -> None:
    """MBS's published Data-record XML shape should produce rows and dates."""
    path = tmp_path / "MBS-XML-20260701.XML"
    path.write_text(
        """<?xml version='1.0' encoding='UTF-8'?>
<MBS_XML><Data><ItemNum>3</ItemNum><Category>1</Category><Group>A1</Group>
<FeeStartDate>01.07.2026</FeeStartDate><ScheduleFee>20.55</ScheduleFee>
<Description>Example item</Description></Data></MBS_XML>""",
        encoding="utf-8",
    )
    records = parse_mbs_xml(
        path,
        source_version="au_mbs_20260701_xml",
        retrieved_at="2026-07-19T00:00:00Z",
    )
    assert len(records) == 1
    assert records[0].item_code == "3"
    assert records[0].effective_from.isoformat() == "2026-07-01"
    assert records[0].payment_amount == 20.55
    assert records[0].provenance.source_version == "au_mbs_20260701_xml"


def test_parse_cms_clfs_fixture(repo_root: Path) -> None:
    """CLFS parser should emit schedule item contracts from CSV fixtures."""
    records = parse_cms_clfs_csv(repo_root / "tests" / "fixtures" / "cms_clfs_fixture.csv")
    assert len(records) == 2
    assert records[0].source_id == "us_cms_clfs"
    assert records[0].code_system == "HCPCS_CLFS"
    assert records[0].payment_amount == 799.5


def test_parse_nhs_genomic_directory_fixture(repo_root: Path) -> None:
    """NHS genomic directory parser should emit coverage-decision contracts."""
    records = parse_nhs_genomic_directory_csv(
        repo_root / "tests" / "fixtures" / "nhs_genomic_directory_fixture.csv"
    )
    assert len(records) == 2
    assert records[0].source_id == "uk_genomic_test_directory"
    assert records[0].decision_status == "covered_with_restrictions"

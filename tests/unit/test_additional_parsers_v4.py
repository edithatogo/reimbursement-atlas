"""Tests for v4 parser expansions."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.parsers import parse_cms_asp_csv, parse_cms_pfs_csv, parse_pbs_csv


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


def test_parse_cms_pfs_fixture(repo_root: Path) -> None:
    """CMS PFS parser should prefer non-facility payment amounts."""
    records = parse_cms_pfs_csv(repo_root / "tests" / "fixtures" / "cms_pfs_fixture.csv")
    assert len(records) == 2
    assert records[1].source_id == "us_cms_pfs"
    assert records[1].item_code == "96040"
    assert records[1].payment_amount == 74.6
    assert records[1].professional_component is True

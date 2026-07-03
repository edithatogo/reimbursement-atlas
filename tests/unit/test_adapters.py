"""Tests for first-wave source adapters."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.adapters import (
    CmsClfsFixtureAdapter,
    MbsXmlFixtureAdapter,
    NhsGenomicDirectoryFixtureAdapter,
    PbsFixtureAdapter,
)


def test_mbs_xml_fixture_adapter_parses_items(repo_root: Path) -> None:
    """The MBS fixture adapter should return normalised schedule records."""
    payload = MbsXmlFixtureAdapter().parse_file(
        repo_root / "tests/fixtures/parsers/mbs_fixture.xml"
    )
    assert len(payload.schedule_items) == 2
    first = payload.schedule_items[0]
    assert first.source_id == "au_mbs"
    assert first.currency == "AUD"
    assert first.payment_amount == 95.60


def test_cms_clfs_fixture_adapter_parses_items(repo_root: Path) -> None:
    """The CMS CLFS fixture adapter should tolerate unpriced contractor-priced rows."""
    payload = CmsClfsFixtureAdapter().parse_file(
        repo_root / "tests/fixtures/parsers/cms_clfs_fixture.csv"
    )
    assert len(payload.schedule_items) == 2
    assert payload.schedule_items[0].payment_amount is None
    assert payload.schedule_items[1].payment_amount == 55.0


def test_pbs_fixture_adapter_parses_items(repo_root: Path) -> None:
    """The PBS fixture adapter should parse published-price placeholders."""
    payload = PbsFixtureAdapter().parse_file(repo_root / "tests/fixtures/parsers/pbs_fixture.csv")
    assert len(payload.schedule_items) == 2
    assert payload.schedule_items[0].domain == "medicines"


def test_nhs_genomic_directory_adapter_parses_coverage(repo_root: Path) -> None:
    """The NHS genomic fixture adapter should produce coverage decision records."""
    payload = NhsGenomicDirectoryFixtureAdapter().parse_file(
        repo_root / "tests/fixtures/parsers/nhs_genomic_directory_fixture.csv"
    )
    assert len(payload.coverage_decisions) == 2
    assert payload.coverage_decisions[0].decision_status == "covered_with_restrictions"

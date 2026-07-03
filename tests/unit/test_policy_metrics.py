"""Tests for policy metrics."""

from __future__ import annotations

from reimburse_atlas.adapters import MbsXmlFixtureAdapter
from reimburse_atlas.policy_metrics import summarise_domain_prices, summarise_transparency
from reimburse_atlas.registry import load_source_registry, project_root


def test_summarise_domain_prices_from_fixture() -> None:
    """Price summaries should group by source/domain/currency."""
    payload = MbsXmlFixtureAdapter().parse_file(
        project_root() / "tests/fixtures/parsers/mbs_fixture.xml"
    )
    summaries = summarise_domain_prices(list(payload.schedule_items))
    assert len(summaries) == 1
    assert summaries[0].priced_item_count == 2
    assert summaries[0].mean_payment_amount is not None


def test_summarise_transparency_has_expected_count() -> None:
    """Transparency summary should cover all registered sources."""
    sources = load_source_registry()
    summary = summarise_transparency(sources)
    assert summary.total_sources == len(sources)
    assert 0.0 <= summary.machine_readable_share <= 1.0

"""Tests for policy demonstrators."""

from __future__ import annotations

from reimburse_atlas.demonstrators import (
    PolicyBrief,
    build_policy_demonstrator_briefs,
    cognitive_procedural_demo,
    genomics_demo,
    medicine_opacity_demo,
)
from reimburse_atlas.parsers import parse_cms_clfs_csv, parse_cms_pfs_csv, parse_mbs_xml
from reimburse_atlas.registry import project_root


def test_genomics_demo_uses_fixtures() -> None:
    root = project_root()
    mbs = parse_mbs_xml(root / "tests/fixtures/mbs_fragment.xml")
    clfs = parse_cms_clfs_csv(root / "tests/fixtures/cms_clfs_fixture.csv")

    result = genomics_demo({"au_mbs": mbs, "us_cms_clfs": clfs})
    assert isinstance(result, PolicyBrief)
    assert result.item_count > 0
    assert result.metric_summary
    assert "Coverage denominator" in result.linkage_summary
    assert "No pooled payment statistic" in result.metric_summary
    assert len(result.caveats) >= 1
    assert any("missing fixture coverage" in caveat.lower() for caveat in result.caveats)


def test_cognitive_procedural_demo_uses_fixtures() -> None:
    root = project_root()
    mbs = parse_mbs_xml(root / "tests/fixtures/mbs_fragment.xml")
    pfs = parse_cms_pfs_csv(root / "tests/fixtures/cms_pfs_fixture.csv")

    result = cognitive_procedural_demo({"au_mbs": mbs, "us_cms_pfs": pfs})
    assert isinstance(result, PolicyBrief)
    assert result.item_count >= 0


def test_medicine_opacity_demo() -> None:
    result = medicine_opacity_demo({})
    assert isinstance(result, PolicyBrief)
    assert result.item_count == 0
    assert "missingness N/A" in result.metric_summary
    assert "No coverage linkage" in result.linkage_summary


def test_build_policy_demonstrator_briefs_returns_three_briefs() -> None:
    root = project_root()
    fixtures = root / "tests" / "fixtures"
    parsed_sources = {
        "au_mbs": parse_mbs_xml(fixtures / "mbs_fragment.xml"),
        "us_cms_clfs": parse_cms_clfs_csv(fixtures / "cms_clfs_fixture.csv"),
        "us_cms_pfs": parse_cms_pfs_csv(fixtures / "cms_pfs_fixture.csv"),
    }

    briefs = build_policy_demonstrator_briefs(parsed_sources)

    assert len(briefs) == 3
    assert {brief.demonstrator_id for brief in briefs} == {
        "genomics_pathology",
        "cognitive_procedural_index",
        "medicine_public_amount_missingness",
    }

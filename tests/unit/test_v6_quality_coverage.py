"""Additional v6 tests for quality gates and analytical helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from reimburse_atlas.adapters.base import AdapterError, non_empty_rows, require_file
from reimburse_atlas.adapters.mbs_xml import MbsXmlFixtureAdapter
from reimburse_atlas.analysis.crosswalk import (
    build_crosswalk_candidates,
    jaccard,
    relationship_for_similarity,
    tokens,
)
from reimburse_atlas.analysis.policy_signals import median_payment_by_source, priced_share
from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord
from reimburse_atlas.ingest import build_first_wave_ingestion_plan, write_ingestion_plan
from reimburse_atlas.ingest.plan import network_policy_for
from reimburse_atlas.ingestion import (
    assess_ingestion_readiness,
    build_first_wave_plans,
    write_ingestion_readiness,
)
from reimburse_atlas.ingestion import (
    write_ingestion_plan as write_acquisition_plan,
)
from reimburse_atlas.models import SourceRecord, SourceVersionRecord
from reimburse_atlas.publication import build_publication_manifest, count_rows
from reimburse_atlas.registry import (
    load_analysis_recipes,
    load_ontology_concepts,
    load_ontology_mapping_templates,
    read_jsonl,
)
from reimburse_atlas.validation import compare_seed_pair, read_csv_rows, read_jsonl_rows


def _source(
    source_id: str = "test_source",
    *,
    access_tier: str = "tier_1",
    machine_readable: bool = True,
    licence_notes: str = "permissive",
    notes: str = "permissive test source",
) -> SourceRecord:
    return SourceRecord.model_validate({
        "id": source_id,
        "jurisdiction": "Testland",
        "system": "Test system",
        "schedule": "Test schedule",
        "domain": "laboratory",
        "access_tier": access_tier,
        "format": "CSV",
        "primary_url": "https://example.org/source.csv",
        "licence_notes": licence_notes,
        "reliability": "high",
        "machine_readable": machine_readable,
        "historical_versions": True,
        "utilisation_data": True,
        "refresh_cadence": "annual",
        "data_owner": "public",
        "tags": ["test"],
        "notes": notes,
    })


def _version(
    source_id: str = "test_source", version_id: str = "test_source_live"
) -> SourceVersionRecord:
    return SourceVersionRecord.model_validate({
        "id": version_id,
        "source_id": source_id,
        "version_label": "Live 2026",
        "source_url": "https://example.org/source.csv",
        "format": "CSV",
        "parser_status": "prototype",
        "notes": "test version",
    })


def _item(
    source_id: str,
    code: str,
    label: str,
    *,
    amount: float | None = None,
    domain: str = "laboratory",
    currency: str | None = "USD",
    description: str | None = None,
) -> ScheduleItemRecord:
    return ScheduleItemRecord(
        source_id=source_id,
        jurisdiction="Testland",
        domain=domain,
        code_system="TEST",
        item_code=code,
        item_label=label,
        item_description=description,
        payment_amount=amount,
        currency=currency,
        provenance=ProvenanceRecord(source_id=source_id),
    )


def test_analysis_crosswalk_branches_are_review_queue_friendly() -> None:
    """The analysis crosswalk helper should expose transparent branch behaviour."""
    assert tokens("The genomic test for rare disease") == frozenset({"genomic", "rare", "disease"})
    assert jaccard(frozenset(), frozenset({"a"})) == pytest.approx(0.0)
    assert relationship_for_similarity(0.95) == "exact"
    assert relationship_for_similarity(0.6) == "related"
    assert relationship_for_similarity(0.1) == "unmapped"

    left = [_item("au_mbs", "A", "rare disease genomic panel")]
    right = [
        _item("us_cms_clfs", "B", "genomic panel for rare disease"),
        _item("us_cms_clfs", "C", "unrelated chemistry assay"),
    ]
    candidates = build_crosswalk_candidates(left, right, threshold=0.2)
    assert [candidate.right_code for candidate in candidates] == ["B"]
    assert candidates[0].evidence_methods == ("token_jaccard",)


def test_policy_signal_summaries_skip_unpriced_records() -> None:
    """Policy signal helpers should report public-price observability by source."""
    records = [
        _item("au_mbs", "1", "consult", amount=10, currency="AUD"),
        _item("au_mbs", "2", "review", amount=20, currency="AUD"),
        _item("au_mbs", "3", "unpriced", amount=None, currency="AUD"),
        _item("us_cms", "A", "test", amount=100, currency="USD"),
    ]
    medians = {row["source_id"]: row for row in median_payment_by_source(records)}
    assert medians["au_mbs"]["median_payment_amount"] == pytest.approx(15)
    assert medians["au_mbs"]["priced_item_count"] == 2
    assert priced_share(records)["au_mbs"] == pytest.approx(0.6667)


def test_adapter_base_rejects_missing_directories_and_empty_rows(tmp_path: Path) -> None:
    """Adapter base guards should fail fast before parser-specific work starts."""
    with pytest.raises(AdapterError):
        require_file(tmp_path / "missing.csv")
    with pytest.raises(AdapterError):
        require_file(tmp_path)
    with pytest.raises(AdapterError):
        non_empty_rows([{"a": ""}], tmp_path / "empty.csv")
    assert non_empty_rows([{"a": "x"}], tmp_path / "ok.csv") == [{"a": "x"}]


def test_mbs_xml_fixture_adapter_error_paths(tmp_path: Path) -> None:
    """The synthetic XML adapter should reject malformed or incomplete fixtures."""
    adapter = MbsXmlFixtureAdapter()
    malformed = tmp_path / "bad.xml"
    malformed.write_text("<schedule><item>", encoding="utf-8")
    with pytest.raises(AdapterError):
        adapter.parse_file(malformed)

    empty = tmp_path / "empty.xml"
    empty.write_text("<schedule />", encoding="utf-8")
    with pytest.raises(AdapterError):
        adapter.parse_file(empty)

    incomplete = tmp_path / "incomplete.xml"
    incomplete.write_text("<schedule><item><code>1</code></item></schedule>", encoding="utf-8")
    with pytest.raises(AdapterError):
        adapter.parse_file(incomplete)


def test_ingest_planning_live_manual_and_write_paths(tmp_path: Path) -> None:
    """Ingestion planning should distinguish fixture, live and manual acquisition modes."""
    live_source = _source("au_mbs")
    manual_source = _source("other_source", access_tier="tier_2", machine_readable=False)
    live_version = _version("au_mbs", "au_mbs_live")
    fixture_version = _version("au_mbs", "au_mbs_fixture")
    manual_version = _version("other_source", "other_source_live")

    assert network_policy_for(live_source, live_version) == "live_fetch_allowed"
    assert network_policy_for(live_source, fixture_version) == "fixture_only"
    assert network_policy_for(manual_source, manual_version) == "manual_download"

    tasks = build_first_wave_ingestion_plan(
        [live_source, manual_source], [live_version, manual_version]
    )
    assert len(tasks) == 1
    jsonl_path, csv_path = write_ingestion_plan(tasks, tmp_path)
    assert jsonl_path.exists()
    assert csv_path.exists()


def test_acquisition_plan_write_paths(tmp_path: Path) -> None:
    """Acquisition-plan writers should produce deterministic CSV and JSONL artefacts."""
    plans = build_first_wave_plans([_source("au_mbs")], [_version("au_mbs", "au_mbs_live")])
    readiness = assess_ingestion_readiness(plans)
    plan_csv, plan_jsonl = write_acquisition_plan(plans, tmp_path)
    ready_csv, ready_jsonl = write_ingestion_readiness(readiness, tmp_path)
    assert plan_csv.exists()
    assert plan_jsonl.exists()
    assert ready_csv.exists()
    assert ready_jsonl.exists()


def test_publication_manifest_excludes_raw_cache_paths(tmp_path: Path) -> None:
    """Publication manifests should warn instead of publishing raw/cache payloads."""
    raw = tmp_path / "data" / "raw_live" / "live.csv"
    raw.parent.mkdir(parents=True)
    raw.write_text("id,value\n1,a\n", encoding="utf-8")
    safe = tmp_path / "data" / "seed" / "safe.jsonl"
    safe.parent.mkdir(parents=True)
    safe.write_text(json.dumps({"id": "x"}) + "\n", encoding="utf-8")

    manifest = build_publication_manifest(
        paths=(Path("data/raw_live/live.csv"), Path("data/seed/safe.jsonl")),
        root=tmp_path,
    )
    assert manifest.artifact_count == 1
    assert manifest.warnings
    assert count_rows(safe) == 1
    assert count_rows(raw) == 1


def test_registry_and_validation_empty_missing_paths(tmp_path: Path) -> None:
    """Missing optional seed files should return empty rows rather than crash."""
    assert load_analysis_recipes(tmp_path / "missing.jsonl") == []
    assert load_ontology_concepts(tmp_path / "missing.jsonl") == []
    assert load_ontology_mapping_templates(tmp_path / "missing.jsonl") == []
    assert read_jsonl_rows(tmp_path / "missing.jsonl") == []
    assert read_csv_rows(tmp_path / "missing.csv") == []

    bad = tmp_path / "bad.jsonl"
    bad.write_text("[]\n", encoding="utf-8")
    with pytest.raises(TypeError):
        read_jsonl(bad)
    with pytest.raises(TypeError):
        read_jsonl_rows(bad)

    status = compare_seed_pair("absent_table", tmp_path)
    assert not status.ok

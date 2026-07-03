"""Unit tests for pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from reimburse_atlas.models import SourceRecord


def test_source_record_rejects_unknown_fields() -> None:
    """Strict pydantic models should reject undeclared fields."""
    payload = {
        "id": "x_source",
        "jurisdiction": "X",
        "system": "X",
        "schedule": "X",
        "domain": "medical_services",
        "access_tier": "tier_1",
        "format": "CSV",
        "primary_url": "https://example.org/data.csv",
        "licence_notes": "Test only.",
        "reliability": "high",
        "machine_readable": True,
        "historical_versions": True,
        "utilisation_data": True,
        "refresh_cadence": "annual",
        "data_owner": "public",
        "tags": ["test"],
        "notes": "Test source.",
        "unexpected": "nope",
    }
    with pytest.raises(ValidationError):
        SourceRecord.model_validate(payload)


def test_source_record_normalises_tags() -> None:
    """Tags should be immutable tuples after validation."""
    record = SourceRecord.model_validate({
        "id": "x_source",
        "jurisdiction": "X",
        "system": "X",
        "schedule": "X",
        "domain": "medical_services",
        "access_tier": "tier_1",
        "format": "CSV",
        "primary_url": "https://example.org/data.csv",
        "licence_notes": "Test only.",
        "reliability": "high",
        "machine_readable": True,
        "historical_versions": True,
        "utilisation_data": True,
        "refresh_cadence": "annual",
        "data_owner": "public",
        "tags": ["A", "B"],
        "notes": "Test source.",
    })
    assert record.tags == ("A", "B")

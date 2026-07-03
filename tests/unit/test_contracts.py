"""Tests for normalised derived-data contracts."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from reimburse_atlas.contracts import CrosswalkCandidate, ProvenanceRecord, ScheduleItemRecord


def test_schedule_item_contract_normalises_currency() -> None:
    """Schedule item records should normalise currency codes."""
    record = ScheduleItemRecord(
        source_id="au_mbs",
        jurisdiction="Australia",
        domain="medical_services",
        code_system="MBS",
        item_code="23",
        item_label="Professional attendance",
        payment_amount=42.85,
        currency="aud",
        effective_from=date(2026, 7, 1),
        provenance=ProvenanceRecord(source_id="au_mbs"),
    )
    assert record.currency == "AUD"


def test_crosswalk_confidence_bounds() -> None:
    """Crosswalk confidence should be bounded between zero and one."""
    with pytest.raises(ValidationError):
        CrosswalkCandidate(
            left_source_id="au_mbs",
            right_source_id="us_cms_pfs",
            left_code="23",
            right_code="99213",
            relationship="related",
            confidence=1.2,
        )

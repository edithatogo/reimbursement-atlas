"""Licence and redistribution gates for source acquisition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from reimburse_atlas.models import SourceRecord

LicenceGateStatus = Literal["green", "amber", "red"]


@dataclass(frozen=True)
class LicenceGate:
    """A source-level gate controlling raw-data mirroring and publication."""

    source_id: str
    status: LicenceGateStatus
    public_dataset_policy: str
    rationale: str


RESTRICTED_MARKERS = (
    "cpt",
    "umls",
    "restricted",
    "copyright",
    "redistribution",
    "confidential",
    "special pricing",
)


def evaluate_licence_gate(source: SourceRecord) -> LicenceGate:
    """Evaluate a cautious licence gate from registry metadata."""
    notes = " ".join([source.licence_notes, source.notes, *source.tags]).lower()
    if any(marker in notes for marker in ("confidential", "restricted", "umls")):
        return LicenceGate(
            source_id=source.id,
            status="red",
            public_dataset_policy="metadata_only_until_legal_review",
            rationale="Registry metadata indicates restricted or confidential content.",
        )
    if any(marker in notes for marker in RESTRICTED_MARKERS):
        return LicenceGate(
            source_id=source.id,
            status="amber",
            public_dataset_policy="derived_fields_only_until_terms_confirmed",
            rationale=(
                "Registry metadata flags redistribution, proprietary descriptors, or price opacity."
            ),
        )
    return LicenceGate(
        source_id=source.id,
        status="green",
        public_dataset_policy="versioned_cache_allowed_after_citation_review",
        rationale="No obvious restriction marker in current registry metadata.",
    )


def evaluate_licence_gates(sources: list[SourceRecord]) -> list[LicenceGate]:
    """Evaluate gates for every registered source."""
    return [evaluate_licence_gate(source) for source in sources]

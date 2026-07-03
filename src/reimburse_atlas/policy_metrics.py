"""Policy-relevant metrics derived from normalised records."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from statistics import mean

from reimburse_atlas.contracts import ScheduleItemRecord
from reimburse_atlas.models import SourceRecord


@dataclass(frozen=True)
class DomainPriceSummary:
    """Simple price summary for one source/domain/currency group."""

    source_id: str
    domain: str
    currency: str
    priced_item_count: int
    mean_payment_amount: float | None


@dataclass(frozen=True)
class TransparencySummary:
    """Source-registry transparency and reproducibility summary."""

    total_sources: int
    machine_readable_share: float
    historical_version_share: float
    utilisation_data_share: float
    access_tier_counts: dict[str, int]


def summarise_domain_prices(items: list[ScheduleItemRecord]) -> list[DomainPriceSummary]:
    """Compute mean payment amounts by source, domain and currency."""
    buckets: dict[tuple[str, str, str], list[float]] = {}
    for item in items:
        if item.payment_amount is None or item.currency is None:
            continue
        key = (item.source_id, item.domain, item.currency)
        buckets.setdefault(key, []).append(item.payment_amount)
    return [
        DomainPriceSummary(
            source_id=source_id,
            domain=domain,
            currency=currency,
            priced_item_count=len(values),
            mean_payment_amount=round(mean(values), 4),
        )
        for (source_id, domain, currency), values in sorted(buckets.items())
    ]


def summarise_transparency(sources: list[SourceRecord]) -> TransparencySummary:
    """Summarise registry-level access/readiness attributes."""
    total = len(sources)
    if total == 0:
        return TransparencySummary(0, 0.0, 0.0, 0.0, {})
    tier_counts = Counter(source.access_tier for source in sources)
    return TransparencySummary(
        total_sources=total,
        machine_readable_share=round(
            sum(1 for source in sources if source.machine_readable) / total,
            4,
        ),
        historical_version_share=round(
            sum(1 for source in sources if source.historical_versions) / total,
            4,
        ),
        utilisation_data_share=round(
            sum(1 for source in sources if source.utilisation_data) / total,
            4,
        ),
        access_tier_counts=dict(sorted(tier_counts.items())),
    )

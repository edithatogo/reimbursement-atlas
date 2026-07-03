"""Small policy-signal prototypes for first-wave analyses."""

from __future__ import annotations

from collections import defaultdict
from statistics import median

from reimburse_atlas.contracts import ScheduleItemRecord


def median_payment_by_source(records: list[ScheduleItemRecord]) -> list[dict[str, object]]:
    """Summarise median public payment by source for comparable fixture slices."""
    grouped: dict[str, list[float]] = defaultdict(list)
    currencies: dict[str, str] = {}
    for record in records:
        if record.payment_amount is None:
            continue
        grouped[record.source_id].append(record.payment_amount)
        if record.currency:
            currencies[record.source_id] = record.currency
    return [
        {
            "source_id": source_id,
            "currency": currencies.get(source_id, ""),
            "priced_item_count": len(amounts),
            "median_payment_amount": median(amounts),
        }
        for source_id, amounts in sorted(grouped.items())
    ]


def priced_share(records: list[ScheduleItemRecord]) -> dict[str, float]:
    """Return share of records with a public numeric amount by source."""
    totals: dict[str, int] = defaultdict(int)
    priced: dict[str, int] = defaultdict(int)
    for record in records:
        totals[record.source_id] += 1
        if record.payment_amount is not None:
            priced[record.source_id] += 1
    return {
        source_id: round(priced[source_id] / total, 4)
        for source_id, total in sorted(totals.items())
        if total > 0
    }

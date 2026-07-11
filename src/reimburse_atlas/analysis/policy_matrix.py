"""Policy signal matrix prototypes for reimbursement schedule comparison."""

from __future__ import annotations

from collections import defaultdict

from reimburse_atlas.contracts import CoverageDecisionRecord, ScheduleItemRecord


def policy_signal_matrix(
    schedule_records: list[ScheduleItemRecord],
    coverage_records: list[CoverageDecisionRecord],
) -> list[dict[str, object]]:
    """Build source-level signals that are useful for policy framing.

    These are deliberately simple, auditable metrics for the first executable
    slice. They should be interpreted as workflow tests until live reviewed
    source files replace the synthetic fixtures.
    """
    by_source: dict[str, list[ScheduleItemRecord]] = defaultdict(list)
    for record in schedule_records:
        by_source[record.source_id].append(record)

    coverage_by_source: dict[str, list[CoverageDecisionRecord]] = defaultdict(list)
    for record in coverage_records:
        coverage_by_source[record.source_id].append(record)

    rows: list[dict[str, object]] = []
    source_ids = sorted(set(by_source) | set(coverage_by_source))
    for source_id in source_ids:
        items = by_source.get(source_id, [])
        decisions = coverage_by_source.get(source_id, [])
        priced_count = sum(item.payment_amount is not None for item in items)
        restricted_count = sum(item.restriction_text is not None for item in items)
        patient_count = sum(item.patient_amount is not None for item in items)
        facility_count = sum(item.facility_component is True for item in items)
        professional_count = sum(item.professional_component is True for item in items)
        restricted_decisions = sum(
            decision.decision_status == "covered_with_restrictions" for decision in decisions
        )
        item_count = len(items)
        decision_count = len(decisions)
        rows.append({
            "source_id": source_id,
            "schedule_item_count": item_count,
            "coverage_decision_count": decision_count,
            "price_observability": _share(priced_count, item_count),
            "item_restriction_share": _share(restricted_count, item_count),
            "patient_amount_observability": _share(patient_count, item_count),
            "professional_component_share": _share(professional_count, item_count),
            "facility_component_share": _share(facility_count, item_count),
            "coverage_restriction_share": _share(restricted_decisions, decision_count),
            "policy_use": _policy_use_label(item_count, decision_count),
        })
    return rows


def _share(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


def _policy_use_label(item_count: int, decision_count: int) -> str:
    if item_count and decision_count:
        return "price_and_coverage_linkage"
    if item_count:
        return "price_schedule_comparison"
    if decision_count:
        return "coverage_architecture_comparison"
    return "not_ready"

"""First policy demonstrators for provenanced, reproducible analyses.

Each demonstrator produces a ``PolicyBrief`` record that can be serialised
to the dashboard, publication manifest or OSF component plan.

Methodological caveats are embedded in the output — never silently removed.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from reimburse_atlas.models import FrozenModel, NonEmptyStr

GENOMICS_EXPECTED_SOURCES = {
    "au_mbs",
    "us_cms_clfs",
    "us_cms_mcd",
    "uk_genomic_test_directory",
}
COGNITIVE_EXPECTED_SOURCES = {"au_mbs", "us_cms_pfs", "ca_on_ohip"}
MEDICINE_EXPECTED_SOURCES = {"au_pbs", "us_cms_asp", "nz_pharmac"}


class PolicyBrief(FrozenModel):
    """A reproducible, caveated policy analysis output."""

    demonstrator_id: NonEmptyStr
    title: NonEmptyStr
    sources_compared: tuple[NonEmptyStr, ...]
    item_count: int
    metric_summary: NonEmptyStr
    caveats: tuple[NonEmptyStr, ...]


def _record_text(record: object, field: str) -> str:
    value = getattr(record, field, "")
    return value.lower() if isinstance(value, str) else ""


def _record_domain(record: object) -> str:
    domain = getattr(record, "domain", None)
    if isinstance(domain, str):
        return domain.lower()
    technology_domain = getattr(record, "technology_domain", None)
    if isinstance(technology_domain, str):
        return technology_domain.lower()
    return ""


def _record_payment_amount(record: object) -> float | None:
    value = getattr(record, "payment_amount", None)
    return float(value) if isinstance(value, (int, float)) else None


def build_policy_demonstrator_briefs(
    parsed_sources: Mapping[str, Sequence[object]],
) -> list[PolicyBrief]:
    """Build all first-policy demonstrator briefs from parsed source fixtures."""
    return [
        genomics_demo(parsed_sources),
        cognitive_procedural_demo(parsed_sources),
        medicine_opacity_demo(parsed_sources),
    ]


def _filter_genomics(
    records: Sequence[object],
) -> list[object]:
    return [
        r
        for r in records
        if _record_domain(r) == "genomics"
        or "genomic" in _record_text(r, "item_label")
        or "genomic" in _record_text(r, "item_description")
        or "genomic" in _record_text(r, "technology_name")
    ]


def _filter_cognitive(records: Sequence[object]) -> list[object]:
    cognitive_keywords = {"consultation", "assessment", "cognitive", "visit", "evaluation"}
    return [
        r for r in records if any(kw in _record_text(r, "item_label") for kw in cognitive_keywords)
    ]


def _filter_procedural(records: Sequence[object]) -> list[object]:
    procedural_keywords = {"procedure", "surgery", "repair", "excision", "injection", "implant"}
    return [
        r for r in records if any(kw in _record_text(r, "item_label") for kw in procedural_keywords)
    ]


def _median_amount(records: Sequence[object]) -> float | None:
    """Return median payment amount across records."""
    amounts = [
        amount for amount in (_record_payment_amount(r) for r in records) if amount is not None
    ]
    if not amounts:
        return None
    amounts.sort()
    n = len(amounts)
    if n % 2 == 1:
        return float(amounts[n // 2])
    return float((amounts[n // 2 - 1] + amounts[n // 2]) / 2.0)


def _percentage_priced(records: Sequence[object]) -> float:
    """Return share of records with a public payment amount."""
    if not records:
        return 0.0
    priced = sum(1 for r in records if _record_payment_amount(r) is not None)
    return round(priced / len(records), 4)


def _missing_sources(
    parsed_sources: Mapping[str, Sequence[object]],
    expected_sources: Iterable[str],
) -> tuple[str, ...]:
    present = set(parsed_sources)
    return tuple(sorted(set(expected_sources) - present))


def genomics_demo(
    parsed_sources: Mapping[str, Sequence[object]],
) -> PolicyBrief:
    """Compare genomics/pathology coverage and pricing across sources."""
    total_items = 0
    all_genomics: list[object] = []
    source_names: list[str] = []

    for source_id, records in parsed_sources.items():
        source_names.append(source_id)
        genomics_items = _filter_genomics(records)
        all_genomics.extend(genomics_items)
        total_items += len(genomics_items)

    median = _median_amount(all_genomics)
    priced_share = _percentage_priced(all_genomics)
    missing_sources = _missing_sources(parsed_sources, GENOMICS_EXPECTED_SOURCES)

    metric = (
        f"Compared genomics items across {len(source_names)} sources; "
        f"{total_items} items found, "
        f"{priced_share * 100:.1f}% priced, "
        f"median payment {median or 'N/A'}."
    )
    caveats = [
        "Genomics domain labels may differ across jurisdictions.",
        "Only items explicitly tagged 'genomics' or containing 'genomic' are compared.",
        "No currency normalisation or PPP adjustment applied.",
    ]
    if missing_sources:
        caveats.append("Missing fixture coverage for: " + ", ".join(missing_sources) + ".")

    return PolicyBrief(
        demonstrator_id="genomics_pathology",
        title="Genomics and pathology coverage and price comparison",
        sources_compared=tuple(sorted(set(source_names))),
        item_count=total_items,
        metric_summary=metric,
        caveats=tuple(caveats),
    )


def cognitive_procedural_demo(
    parsed_sources: Mapping[str, Sequence[object]],
) -> PolicyBrief:
    """Estimate cognitive versus procedural fee relativities."""
    all_cognitive: list[object] = []
    all_procedural: list[object] = []
    source_names: list[str] = []

    for source_id, records in parsed_sources.items():
        source_names.append(source_id)
        all_cognitive.extend(_filter_cognitive(records))
        all_procedural.extend(_filter_procedural(records))

    cog_median = _median_amount(all_cognitive)
    proc_median = _median_amount(all_procedural)
    ratio: float | None = (
        round(proc_median / cog_median, 4)
        if cog_median and proc_median and cog_median > 0
        else None
    )
    missing_sources = _missing_sources(parsed_sources, COGNITIVE_EXPECTED_SOURCES)

    metric = (
        f"Cognitive items: {len(all_cognitive)} (median {cog_median or 'N/A'}), "
        f"Procedural items: {len(all_procedural)} (median {proc_median or 'N/A'}), "
        f"Ratio (proc/cog): {ratio or 'N/A'}."
    )
    caveats = [
        "Keyword-based cognitive/procedural classification is a prototype heuristic.",
        "No case-mix or complexity adjustment applied.",
        "Currency and purchasing-power differences are not normalised.",
    ]
    if missing_sources:
        caveats.append("Missing fixture coverage for: " + ", ".join(missing_sources) + ".")

    return PolicyBrief(
        demonstrator_id="cognitive_procedural_index",
        title="Cognitive versus procedural fee relativities",
        sources_compared=tuple(sorted(set(source_names))),
        item_count=len(all_cognitive) + len(all_procedural),
        metric_summary=metric,
        caveats=tuple(caveats),
    )


def medicine_opacity_demo(
    parsed_sources: Mapping[str, Sequence[object]],
) -> PolicyBrief:
    """Characterise medicine price opacity across jurisdictions."""
    total_items = 0
    priced_count = 0
    source_names: list[str] = []

    for source_id, records in parsed_sources.items():
        source_names.append(source_id)
        for r in records:
            domain = _record_domain(r)
            if "medicine" in domain or "drug" in domain:
                total_items += 1
                if _record_payment_amount(r) is not None:
                    priced_count += 1

    opacity = round(1.0 - (priced_count / total_items if total_items > 0 else 0.0), 4)
    missing_sources = _missing_sources(parsed_sources, MEDICINE_EXPECTED_SOURCES)

    metric = (
        f"Medicine items across {len(source_names)} sources; "
        f"{total_items} items, {priced_count} with public price, "
        f"opacity index {opacity} (lower = more transparent)."
    )
    caveats = [
        "Medicine price opacity reflects only public schedule amounts, not rebates.",
        "List prices may overstate net reimbursement.",
        "No confidential discount or bundled-payment adjustment applied.",
    ]
    if missing_sources:
        caveats.append("Missing fixture coverage for: " + ", ".join(missing_sources) + ".")

    return PolicyBrief(
        demonstrator_id="medicine_opacity_index",
        title="Medicine price-opacity scorecard",
        sources_compared=tuple(sorted(set(source_names))),
        item_count=total_items,
        metric_summary=metric,
        caveats=tuple(caveats),
    )

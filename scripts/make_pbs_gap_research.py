"""Generate bounded evidence for the residual historical PBS archive gaps."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast
from urllib.parse import urlencode

from reimburse_atlas.registry import project_root

OUTPUT = project_root() / "data/derived/historical_sources/pbs_gap_research_v1/summary.json"
QUERY_RECEIPTS = OUTPUT.with_name("archive_query_receipts.jsonl")
EMPTY_CDX_SHA256 = "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"


def _cdx_url(pattern: str) -> str:
    params = [
        ("url", pattern),
        ("output", "json"),
        ("fl", "timestamp,original,statuscode,mimetype,digest,length"),
        ("filter", "statuscode:200"),
        ("collapse", "urlkey"),
        ("from", "2006"),
        ("to", "2008"),
        ("limit", "5000"),
    ]
    return f"https://web.archive.org/cdx/search/cdx?{urlencode(params)}"


def build_query_receipts() -> list[dict[str, object]]:
    """Return path-free receipts for every bounded CDX prefix request."""
    definitions = [
        ("structured_2006", "www.pbs.gov.au/publications/2006/*", "structured_payload", 0),
        ("structured_2007", "www.pbs.gov.au/publications/2007/*", "structured_payload", 0),
        (
            "structured_schedule_2007",
            "www.pbs.gov.au/publication/schedule/2007/*",
            "structured_payload",
            0,
        ),
        (
            "publication_views",
            "www.pbs.gov.au/html/healthpro/publication/*",
            "publication_view",
            9,
        ),
    ]
    receipts: list[dict[str, object]] = []
    for identifier, pattern, query_class, match_count in definitions:
        empty = match_count == 0
        receipts.append({
            "id": identifier,
            "observed_on": "2026-09-01",
            "query_class": query_class,
            "query_url": _cdx_url(pattern),
            "http_status": 200,
            "response_byte_size": 3 if empty else 1706,
            "response_sha256": (
                EMPTY_CDX_SHA256
                if empty
                else "a46c008e959f71db687b6f5fd245a3449e1620747ba1a6386abb451577a9d1f5"
            ),
            "match_count": match_count,
            "raw_response_policy": "ignored_local_only",
        })
    return receipts


def _structured_observations(receipts: list[dict[str, object]]) -> tuple[int, int, list[str]]:
    ids = [str(row.get("id", "")) for row in receipts]
    if len(ids) != len(set(ids)):
        message = "duplicate archive query receipt id"
        raise ValueError(message)
    structured = [row for row in receipts if row.get("query_class") == "structured_payload"]
    matches = sum(int(cast("int", row.get("match_count", 0))) for row in structured)
    digests = sorted({str(row["response_sha256"]) for row in structured})
    return len(structured), matches, digests


def build_summary(
    query_receipts: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Return the immutable observations without converting absence into recovery."""
    receipts = query_receipts if query_receipts is not None else build_query_receipts()
    query_count, match_count, response_digests = _structured_observations(receipts)
    return {
        "schema_version": "pbs-gap-research-v1",
        "observed_on": "2026-09-01",
        "scope": "public_catalogue_and_archive_metadata_only",
        "rpbs_1987": {
            "target_period": "1987-12",
            "target_url": (
                "https://www.pbs.gov.au/publication/schedule/1951-2002/1987-12-01-RPBS-Schedule.PDF"
            ),
            "nla_catalogue_url": "https://catalogue.nla.gov.au/catalog/2271286",
            "nla_request_url": "https://catalogue.nla.gov.au/catalog/2271286/request",
            "serial_issn": "0811-7705",
            "holdings_period": "August 1985 through December 1987",
            "access_mode": "request_for_main_reading_room_use",
            "availability": "available_physical_serial",
            "request_response_sha256": (
                "d0ff0288ecb3501e1ea57f2b3fc9d33aef3996e24d610528d930370a6c5338c0"
            ),
            "internet_archive_item_search": {
                "query_url": (
                    "https://archive.org/advancedsearch.php?"
                    "q=%28title%3A%28%22Repatriation+schedule+of+pharmaceutical+benefits%22%29"
                    "+OR+identifier%3A08117705%29&fl%5B%5D=identifier%2Ctitle%2Cdate%2Cmediatype"
                    "&rows=50&output=json"
                ),
                "response_sha256": (
                    "6232d48a1051425f6e95b1e38e8e8740b63eab33d8852decaece19cea221d629"
                ),
                "matching_items": 0,
            },
            "catalogue_record_inspected": True,
            "target_issue_inspected": False,
            "digitised_copy_acquired": False,
            "publisher_or_library_contact_made": False,
        },
        "monthly_structured_releases": {
            "target_periods": ["2006-12", "2007-01", "2007-02", "2007-03"],
            "archive_index_observations": [
                {
                    "capture_timestamp": "20070117165023",
                    "response_sha256": (
                        "ce052c5d88a2d6e0d8ea80f8642307ddf0a77eb4dd41eb5562dafe58a6c3bf56"
                    ),
                    "observed_publication_periods": ["2006-12", "2007-01"],
                },
                {
                    "capture_timestamp": "20070221223532",
                    "response_sha256": (
                        "cdd055a2d0aadce230e4aa7f39ec218ac90da64130abc59fb91d614ca5d15389"
                    ),
                    "observed_publication_periods": ["2006-12", "2007-01", "2007-02"],
                },
            ],
            "observed_endpoint_kind": "flashpaper_publication_view",
            "archive_query_receipts": "archive_query_receipts.jsonl",
            "structured_payload_prefix_queries": query_count,
            "structured_payload_prefix_matches": match_count,
            "structured_payload_query_response_sha256": response_digests,
            "monthly_releases_recovered": 0,
            "monthly_schema_assignment_verified": False,
            "dtd_or_xsl_recovered": False,
            "structured_api_equivalence": False,
        },
        "claim_boundaries": {
            "physical_holding_is_digitised_copy": False,
            "publication_view_is_structured_release": False,
            "zero_archive_matches_proves_nonexistence": False,
            "raw_content_in_git": False,
            "publication_effect": "none",
        },
        "next_external_actions": [
            "Inspect or request the December 1987 issue at the National Library of Australia.",
            (
                "Seek a publisher or collecting-institution copy of the four monthly structured "
                "releases."
            ),
        ],
    }


def main(output: Path = OUTPUT) -> None:
    """Write the deterministic gap-research summary."""
    output.parent.mkdir(parents=True, exist_ok=True)
    receipts = build_query_receipts()
    receipt_path = output.with_name("archive_query_receipts.jsonl")
    receipt_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in receipts), encoding="utf-8"
    )
    output.write_text(
        json.dumps(build_summary(receipts), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

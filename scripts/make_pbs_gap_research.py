"""Generate bounded evidence for the residual historical PBS archive gaps."""

from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.registry import project_root

OUTPUT = project_root() / "data/derived/historical_sources/pbs_gap_research_v1/summary.json"


def build_summary() -> dict[str, object]:
    """Return the immutable observations without converting absence into recovery."""
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
            "structured_payload_prefix_queries": 3,
            "structured_payload_prefix_matches": 0,
            "structured_payload_query_response_sha256": (
                "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"
            ),
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
    output.write_text(
        json.dumps(build_summary(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

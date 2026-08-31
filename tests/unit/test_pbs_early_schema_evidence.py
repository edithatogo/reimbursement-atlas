"""Offline checks for bounded, metadata-only early PBS schema evidence."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "data/derived/historical_sources/pbs_early_schema_recovery"
SUMMARY = json.loads((EVIDENCE / "summary.json").read_text(encoding="utf-8"))
RECEIPTS = [
    json.loads(line)
    for line in (EVIDENCE / "acquisition_receipts.jsonl").read_text(encoding="utf-8").splitlines()
]


def test_schema_receipts_bind_exact_source_identity_and_verification():
    expected = {
        "1.1.1": (
            "2006-11-29",
            5289495,
            "728d2999fc2311317634013d9b30637d0d041391efd55914bada8e71a3ad5388",
            19,
        ),
        "1.2": (
            "2007-02-06",
            4600602,
            "b1a8aaa788bc962e1be65605e204e311648f37bc3d7800cc73a5e7c2e3e00ae9",
            22,
        ),
    }
    assert len(RECEIPTS) == len({row["id"] for row in RECEIPTS}) == 2
    assert {row["schema_version"] for row in RECEIPTS} == set(expected)
    for row in RECEIPTS:
        version = row["schema_version"]
        source_date, size, digest, parsed_count = expected[version]
        assert row["source_url"] == (
            f"https://data.pbs.gov.au/download/schema-archive/v1/v{version}.zip"
        )
        assert row["source_index_url"] == SUMMARY["source_index"]["url"]
        assert row["artifact_kind"] == "schema_distribution"
        assert row["source_id"] == "au_pbs"
        assert row["source_date_basis"] == "official_schema_archive_index"
        assert date.fromisoformat(row["source_date"]) == date.fromisoformat(source_date)
        assert datetime.fromisoformat(row["acquired_at"]).tzinfo is not None
        assert (row["byte_size"], row["checksum_sha256"]) == (size, digest)
        assert re.fullmatch(r"[0-9a-f]{64}", row["checksum_sha256"])
        assert (row["http_status"], row["acquisition_status"]) == (200, "acquired")
        verification = row["verification"]
        assert verification["zip_signature"] == "504b0304"
        assert verification["outer_zip_crc"] == verification["nested_zip_crc"] == "passed"
        assert "testzip()" in verification["crc_method"]
        assert "ElementTree.fromstring()" in verification["xml_method"]
        assert verification["xml_well_formedness"] == "passed"
        assert verification["xml_documents_parsed"] == parsed_count
        assert verification["xml_parse_errors"] == 0
        assert verification["internal_basic_schema_version"] == version
        assert verification["schema_compilation"] == "not_performed"
        assert verification["monthly_release_schema_validation"] == "not_performed"
        assert verification["archive_payload_digest_verified"] is False
        assert row["sample_xml_classification"] == "illustrative_hand_edited_schema_examples"
        for field in (
            "sample_xml_is_monthly_release_evidence",
            "monthly_release_recovered",
            "rpbs_1987_pdf_recovered",
            "raw_content_in_git",
        ):
            assert row[field] is False


def test_summary_keeps_monthly_pdf_and_integration_claims_separate():
    assert SUMMARY["schema_version"] == "pbs-early-schema-recovery-v1"
    assert SUMMARY["evidence_scope"] == "bounded_public_metadata_only"
    assert SUMMARY["integration_status"] == "isolated_local_commit_for_parent_integration_after_801"
    assert SUMMARY["acquisition_receipts"] == "acquisition_receipts.jsonl"
    assert SUMMARY["counts"] == {
        "recovered_schema_packages": len(RECEIPTS),
        "recovered_monthly_releases": 0,
        "recovered_rpbs_1987_pdfs": 0,
        "cdx_verified_archive_indexes": 3,
    }
    required_boundaries = {
        "sample_xml_is_monthly_release_evidence",
        "monthly_release_schema_assignment_verified",
        "missing_month_amendments_recovered",
        "standalone_dtd_or_xsl_recovered",
        "structured_api_equivalence",
        "archive_schema_payload_digest_verified",
        "nla_target_issue_inspected",
        "raw_content_in_git",
        "publisher_contact_made",
        "uploaded_or_published",
        "exhaustive_archive_absence_proven",
    }
    assert set(SUMMARY["claim_boundaries"]) == required_boundaries
    assert all(value is False for value in SUMMARY["claim_boundaries"].values())
    assert SUMMARY["unresolved_targets"]["monthly_releases"] == [
        "2006-12",
        "2007-01",
        "2007-02",
        "2007-03",
    ]


def test_archive_digests_and_nla_lead_do_not_become_payload_claims():
    indexes = SUMMARY["archive_index_verifications"]
    assert len(indexes) == len({row["capture_timestamp"] for row in indexes}) == 3
    for row in indexes:
        assert row["artifact_kind"] == "archive_index_html"
        assert row["verification_scope"] == "index_html_only_not_linked_payloads"
        assert row["checksum_match"] is True
        assert row["cdx_digest_sha1_base32"] == row["replay_digest_sha1_base32"]
        assert re.fullmatch(r"[A-Z2-7]{32}", row["cdx_digest_sha1_base32"])
        for key in ("checksum_sha256", "cdx_response_checksum_sha256"):
            assert re.fullmatch(r"[0-9a-f]{64}", row[key])
        assert row["byte_size"] > 0
        assert "hashlib.sha1" in row["verification_method"]
        assert urlsplit(row["cdx_query_url"]).hostname == "web.archive.org"
        assert row["replay_url"] == (
            f"https://web.archive.org/web/{row['capture_timestamp']}id_/{row['original_url']}"
        )
    lead = SUMMARY["nla_holdings_lead"]
    assert lead["catalogue_url"] == "https://catalogue.nla.gov.au/catalog/2271286"
    assert lead["holdings_url"] == lead["catalogue_url"] + "/request"
    assert lead["call_number"] == "N 615.10994 REP"
    assert lead["serial_issn"] == "0811-7705"
    assert lead["target_edition"] == "1987-12"
    assert lead["holdings_periods"] == [
        "1983 no. 1 through 1985 no. 2",
        "August 1985 through December 1987",
    ]
    assert lead["evidence_class"] == "physical_serial_holdings_lead_only"
    for field in ("target_issue_inspected", "digitised_copy_acquired", "order_or_contact_made"):
        assert lead[field] is False


def test_public_metadata_contains_no_local_paths_or_raw_markup():
    paths = [
        EVIDENCE / "summary.json",
        EVIDENCE / "acquisition_receipts.jsonl",
        ROOT / "docs/PBS_EARLY_SCHEMA_RECOVERY.md",
    ]
    forbidden = ("/Users/", "/Volumes/", "file://", "data/raw", "<?xml", "<pbs:", "<!DOCTYPE")
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert all(token not in text for token in forbidden)
    assert {path.name for path in EVIDENCE.iterdir()} == {
        "summary.json",
        "acquisition_receipts.jsonl",
    }

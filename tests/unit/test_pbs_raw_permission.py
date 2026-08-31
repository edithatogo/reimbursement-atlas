"""PBS source permission stays distinct from publication and other source rights."""

import json
from pathlib import Path
from typing import Any, cast

import pytest

from reimburse_atlas.licence_review import (
    PBSRawPermission,
    pbs_raw_permission_status,
    pbs_raw_redistribution_status,
)
from reimburse_atlas.registry import project_root

VALID_PATH = "/publication/schedule/2026/07/2026-07-01-general-schedule.pdf"


@pytest.mark.parametrize("host", ["www.pbs.gov.au", "m.pbs.gov.au", "data.pbs.gov.au"])
def test_owner_attestation_allows_pbs_without_per_file_approval(host: str) -> None:
    assert pbs_raw_redistribution_status(f"https://{host}{VALID_PATH}") == (
        "allowed_owner_attested_permission"
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://www.cms.gov/file.pdf",
        "https://www.mbsonline.gov.au/file.pdf",
        "https://www.pbs.gov.au.example.com/file.pdf",
        "https://www.pbs.gov.au@evil.example/file.pdf",
        "file:///data/raw_live/file.pdf",
        "https://user:secret@www.pbs.gov.au/file.pdf",
        "https://[malformed/file.pdf",
        "https://www.pbs.gov.au/news/2026/general-schedule.pdf",
        "https://www.pbs.gov.au/publication/schedule/2026/07/terms.pdf",
        "https://www.pbs.gov.au/publication/schedule/2026/07/general-schedule.html",
        "https://www.pbs.gov.au/publication/schedule/2026/07/updated-pbs-text-files.pdf",
        "https://www.pbs.gov.au/publication/schedule/2026/07/../general-schedule.pdf",
        "https://www.pbs.gov.au/publication/schedule/2026/07/%2e%2e/general-schedule.pdf",
        "https://www.pbs.gov.au:invalid/publication/schedule/2026/07/general-schedule.pdf",
        "https://www.pbs.gov.au:8080/publication/schedule/2026/07/general-schedule.pdf",
        f"https://www.pbs.gov.au{VALID_PATH}?download=other",
        f"https://www.pbs.gov.au{VALID_PATH}#other",
    ],
)
def test_permission_does_not_clear_other_sources_or_credentials(url: str) -> None:
    assert pbs_raw_redistribution_status(url) == "outside_pbs_permission_scope"


def test_missing_permission_record_is_not_approval(tmp_path: Path) -> None:
    assert pbs_raw_permission_status(root=tmp_path) == ("blocked_pending_explicit_permission")


@pytest.mark.parametrize("content", ["invalid", "[]", "{}", '{"decision":"revoked"}'])
def test_malformed_or_revoked_permission_is_not_approval(tmp_path: Path, content: str) -> None:
    path = tmp_path / "data/licence_review/pbs_raw_permission.json"
    path.parent.mkdir(parents=True)
    path.write_text(content)
    assert pbs_raw_permission_status(root=tmp_path) == ("blocked_pending_explicit_permission")


@pytest.fixture
def permission_record() -> dict[str, Any]:
    path = project_root() / "data/licence_review/pbs_raw_permission.json"
    return cast("dict[str, Any]", json.loads(path.read_text()))


def write_permission(root: Path, record: dict[str, Any]) -> None:
    path = root / "data/licence_review/pbs_raw_permission.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record))


@pytest.mark.parametrize("field", list(PBSRawPermission.model_fields))
def test_every_permission_field_is_required(
    tmp_path: Path, permission_record: dict[str, Any], field: str
) -> None:
    del permission_record[field]
    write_permission(tmp_path, permission_record)
    assert pbs_raw_permission_status(root=tmp_path) == "blocked_pending_explicit_permission"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("permission_status", "revoked"),
        ("revoked_at", "2026-08-31"),
        ("owner_statements", ["", " "]),
        ("preservation_controls", []),
        ("exclusions", []),
        ("recorded_at", "not-a-date"),
        ("per_file_owner_approval_required", 0),
        ("per_file_owner_approval_required", True),
        ("publisher_permission_document_verified", True),
        ("publication_state", "published"),
        ("licence_identifier", "Apache-2.0"),
        ("scope", "all PBS website content"),
    ],
)
def test_invalid_or_broadened_record_fails_closed(
    tmp_path: Path, permission_record: dict[str, Any], field: str, value: object
) -> None:
    permission_record[field] = value
    write_permission(tmp_path, permission_record)
    assert pbs_raw_permission_status(root=tmp_path) == "blocked_pending_explicit_permission"


@pytest.mark.parametrize(
    "name",
    [
        "2026-07-01-xml-V3.zip",
        "2026-07-01-V2extracts.zip",
        "2026-07-01-V2SOextracts.zip",
        "1-supply-only-listings-july-2026-public.csv",
    ],
)
def test_structured_categories_are_allowed(name: str) -> None:
    assert (
        pbs_raw_redistribution_status(
            f"https://www.pbs.gov.au/publication/schedule/2026/07/{name}?variant=3"
        )
        == "allowed_owner_attested_permission"
    )


def test_summary_record_permission_does_not_approve_copyright_page() -> None:
    assert pbs_raw_permission_status() == "allowed_owner_attested_permission"
    assert (
        pbs_raw_redistribution_status("https://www.pbs.gov.au/info/general/copyright")
        == "outside_pbs_permission_scope"
    )


def test_historical_consolidated_schedules_are_within_scope() -> None:
    assert (
        pbs_raw_redistribution_status(
            "https://www.pbs.gov.au/publication/schedule/1951-2002/1986-11-01-consolidated-schedules.pdf"
        )
        == "allowed_owner_attested_permission"
    )


@pytest.mark.parametrize(
    ("field", "first_value", "last_value"),
    [
        ("permission_status", "revoked", "active"),
        ("permission_status", "active", "revoked"),
        ("revoked_at", "2026-08-31", None),
        ("revoked_at", None, "2026-08-31"),
        ("permission_status", "active", "active"),
    ],
)
def test_duplicate_permission_keys_fail_closed(
    tmp_path: Path,
    permission_record: dict[str, Any],
    field: str,
    first_value: object,
    last_value: object,
) -> None:
    del permission_record[field]
    content = json.dumps(permission_record)[:-1] + (
        f", {json.dumps(field)}: {json.dumps(first_value)},"
        f" {json.dumps(field)}: {json.dumps(last_value)}}}"
    )
    path = tmp_path / "data/licence_review/pbs_raw_permission.json"
    path.parent.mkdir(parents=True)
    path.write_text(content)
    assert pbs_raw_permission_status(root=tmp_path) == "blocked_pending_explicit_permission"
    assert (
        pbs_raw_redistribution_status(f"https://www.pbs.gov.au{VALID_PATH}", root=tmp_path)
        == "blocked_pending_explicit_permission"
    )


@pytest.mark.parametrize(
    "name",
    [
        "general-terms.pdf",
        "not-a-schedule-guide.pdf",
        "xml-documentation.txt",
        "2026-07-01-general-terms.pdf",
        "2026-07-01-not-a-schedule-guide.pdf",
        "2026-07-01-xml-documentation.txt",
        "prefix-2026-07-01-general-schedule.pdf",
        "2026-07-01-general-schedule-guide.pdf",
        "2026-07-01-general-schedule.zip",
        "2026-07-01-xml-V3.pdf",
    ],
)
def test_arbitrary_keyword_filenames_are_not_permission(name: str) -> None:
    assert (
        pbs_raw_redistribution_status(f"https://www.pbs.gov.au/publication/schedule/2026/07/{name}")
        == "outside_pbs_permission_scope"
    )


@pytest.mark.parametrize(
    ("inventory", "allowed_count", "excluded_count"),
    [
        ("historical_pbs_structured_archive_targets.jsonl", 655, 0),
        ("historical_pbs_archive_targets.jsonl", 1048, 1),
    ],
)
def test_reviewed_inventory_filename_coverage(
    tmp_path: Path,
    permission_record: dict[str, Any],
    inventory: str,
    allowed_count: int,
    excluded_count: int,
) -> None:
    write_permission(tmp_path, permission_record)
    rows = [
        json.loads(line)
        for line in (project_root() / "data/seed" / inventory).read_text().splitlines()
        if line
    ]
    allowed = excluded = 0
    for row in rows:
        notice = row["file_name"].lower() == "updated-pbs-text-files.pdf"
        expected = "outside_pbs_permission_scope" if notice else "allowed_owner_attested_permission"
        assert pbs_raw_redistribution_status(row["file_url"], root=tmp_path) == expected, row[
            "file_url"
        ]
        excluded += notice
        allowed += not notice
    assert (allowed, excluded) == (allowed_count, excluded_count)


def test_reviewed_filename_families_generalize_case_and_numeric_runs() -> None:
    assert (
        pbs_raw_redistribution_status(
            "https://www.pbs.gov.au/publication/schedule/2027/08/2027-08-02-XML-v42.zip"
        )
        == "allowed_owner_attested_permission"
    )

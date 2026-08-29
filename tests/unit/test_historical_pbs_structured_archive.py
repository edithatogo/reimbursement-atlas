"""Tests for official structured PBS archive discovery."""

from __future__ import annotations

import re

import pytest

from scripts import discover_historical_pbs_structured_archive as structured


def test_discovery_separates_structured_packages_from_pdfs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    links = [
        "https://www.pbs.gov.au/publication/schedule/2025/01/pbs-api-csv.zip?variant=3",
        "https://www.pbs.gov.au/publication/schedule/2025/01/pbs-xml.zip?variant=3",
        "https://www.pbs.gov.au/publication/schedule/2025/01/general.pdf?variant=3",
        "https://example.com/not-official.zip",
    ]
    monkeypatch.setattr(structured, "fetch_links", lambda _url: links)

    rows = structured.discover(year=2003)

    assert len(rows) == 2
    assert {row["structured_format"] for row in rows} == {"csv_zip", "xml_zip"}
    assert all(row["file_kind"] == "zip" for row in rows)
    assert all(row["download_policy"] == "download_for_local_review" for row in rows)
    assert all(re.fullmatch(r"[a-z0-9_]+", str(row["source_version_id"])) for row in rows)


def test_unknown_zip_is_excluded_from_machine_readable_inventory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    link = "https://www.pbs.gov.au/publication/schedule/2008/archive-package.zip?variant=3"
    monkeypatch.setattr(structured, "fetch_links", lambda _url: [link])

    assert structured.discover(year=2003) == []

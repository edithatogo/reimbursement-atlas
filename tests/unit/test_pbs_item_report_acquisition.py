from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import acquire_pbs_item_report
from scripts.acquire_pbs_item_report import EXPECTED_LICENCE, acquire, normalize_package


def _payload() -> dict[str, object]:
    return {
        "success": True,
        "result": {
            "license_title": EXPECTED_LICENCE,
            "metadata_modified": "2023-08-10T00:58:09Z",
            "title": "Pharmaceutical Benefits Scheme (PBS) - Item Report",
            "resources": [
                {
                    "format": "CSV",
                    "id": "resource-1",
                    "last_modified": "2016-08-29T00:00:00",
                    "name": "CSV PBS Item Report",
                    "url": "https://data.gov.au/data/dataset/example/download/report.csv",
                }
            ],
        },
    }


def test_normalize_package_preserves_rights_and_source_identity() -> None:
    summary, resources = normalize_package(_payload())

    assert summary["licence"] == EXPECTED_LICENCE
    assert summary["resource_count"] == 1
    assert summary["temporal_coverage"] == "1992-2016 YTD"
    assert resources[0]["source_url"].startswith("https://data.gov.au/")


def test_normalize_package_fails_closed_on_licence_drift() -> None:
    payload = _payload()
    payload["result"]["license_title"] = "Unknown"  # type: ignore[index]

    with pytest.raises(ValueError, match="licence"):
        normalize_package(payload)


def test_normalize_package_rejects_non_authoritative_resource_host() -> None:
    payload = _payload()
    payload["result"]["resources"][0]["url"] = "https://example.invalid/report.csv"  # type: ignore[index]

    with pytest.raises(ValueError, match="Unapproved resource URL"):
        normalize_package(payload)


def test_acquire_rejects_html_disguised_as_csv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, resources = normalize_package(_payload())

    def html_response(_: str) -> bytes:
        return b"<html>error</html>"

    monkeypatch.setattr(acquire_pbs_item_report, "_read_url", html_response)

    with pytest.raises(ValueError, match="Invalid CSV signature"):
        acquire(
            resources,
            raw_dir=tmp_path / "raw",
            previous_receipts_path=tmp_path / "absent.jsonl",
        )


def test_acquire_refreshes_cache_when_catalogue_metadata_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, resources = normalize_package(_payload())
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    cache = raw_dir / "resource-1.csv"
    cache.write_text(
        "Year,Item_number,State,Scheme,Month,Patient_Category,Services,Benefits ($)\n"
        "2015,1,NSW,PBS,January,General,1,1\n",
        encoding="utf-8",
    )
    previous_path = tmp_path / "resources.jsonl"
    previous_path.write_text(
        json.dumps({**resources[0], "last_modified": "older"}) + "\n", encoding="utf-8"
    )
    fresh = (
        b"Year,Item_number,State,Scheme,Month,Patient_Category,Services,Benefits ($)\n"
        b"2016,2,VIC,PBS,February,General,2,2\n"
    )

    def fresh_response(_: str) -> bytes:
        return fresh

    monkeypatch.setattr(acquire_pbs_item_report, "_read_url", fresh_response)

    receipts = acquire(resources, raw_dir=raw_dir, previous_receipts_path=previous_path)

    assert cache.read_bytes() == fresh
    assert receipts[0]["status"] == "refreshed_validated"

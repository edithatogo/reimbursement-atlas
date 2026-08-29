from __future__ import annotations

import pytest

from scripts.acquire_pbs_item_report import EXPECTED_LICENCE, normalize_package


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

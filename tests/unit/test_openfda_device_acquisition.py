from urllib.parse import parse_qs, urlparse

import pytest

from reimburse_atlas.openfda_device_acquisition import (
    OpenFdaAcquisitionError,
    acquire_complete_device_classifications,
)


def _fetch(url: str) -> dict[str, object]:
    query = parse_qs(urlparse(url).query)
    skip = int(query["skip"][0])
    rows = [
        {"product_code": f"{index:03d}", "device_name": f"Device {index}"}
        for index in range(skip, min(skip + 2, 5))
    ]
    return {
        "meta": {"results": {"skip": skip, "limit": 2, "total": 5}},
        "results": rows,
    }


def test_complete_openfda_acquisition_is_deterministic() -> None:
    payload, summary = acquire_complete_device_classifications(
        fetch_json=_fetch,
        page_size=2,
    )
    assert summary["status"] == "complete"
    assert summary["record_count"] == 5
    assert summary["page_count"] == 3
    assert [row["product_code"] for row in payload["results"]] == [
        "000",
        "001",
        "002",
        "003",
        "004",
    ]


def test_openfda_acquisition_rejects_total_drift() -> None:
    def drifting_fetch(url: str) -> dict[str, object]:
        page = _fetch(url)
        if parse_qs(urlparse(url).query)["skip"][0] != "0":
            page["meta"]["results"]["total"] = 6
        return page

    with pytest.raises(OpenFdaAcquisitionError, match="total changed"):
        acquire_complete_device_classifications(
            fetch_json=drifting_fetch,
            page_size=2,
        )

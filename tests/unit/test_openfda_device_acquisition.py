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


@pytest.mark.parametrize("page_size", [0, 1001])
def test_openfda_acquisition_rejects_invalid_page_size(page_size: int) -> None:
    with pytest.raises(OpenFdaAcquisitionError, match="page_size"):
        acquire_complete_device_classifications(page_size=page_size)


def test_openfda_acquisition_rejects_duplicate_product_codes() -> None:
    def duplicate_fetch(_url: str) -> dict[str, object]:
        return {
            "meta": {"results": {"total": 2, "skip": 0}},
            "results": [{"product_code": "AAA"}, {"product_code": "AAA"}],
        }

    with pytest.raises(OpenFdaAcquisitionError, match="duplicate"):
        acquire_complete_device_classifications(fetch_json=duplicate_fetch, page_size=2)


def test_openfda_acquisition_rejects_empty_page() -> None:
    def empty_fetch(_url: str) -> dict[str, object]:
        return {"meta": {"results": {"total": 2, "skip": 0}}, "results": []}

    with pytest.raises(OpenFdaAcquisitionError, match="page metadata"):
        acquire_complete_device_classifications(fetch_json=empty_fetch, page_size=2)


def test_openfda_acquisition_rejects_skip_drift() -> None:
    def drifted_fetch(_url: str) -> dict[str, object]:
        return {
            "meta": {"results": {"total": 1, "skip": 1}},
            "results": [{"product_code": "AAA"}],
        }

    with pytest.raises(OpenFdaAcquisitionError, match="page metadata"):
        acquire_complete_device_classifications(fetch_json=drifted_fetch, page_size=1)


def test_openfda_acquisition_rejects_missing_product_code() -> None:
    def missing_code_fetch(_url: str) -> dict[str, object]:
        return {
            "meta": {"results": {"total": 1, "skip": 0}},
            "results": [{"product_code": ""}],
        }

    with pytest.raises(OpenFdaAcquisitionError, match="missing"):
        acquire_complete_device_classifications(fetch_json=missing_code_fetch, page_size=1)

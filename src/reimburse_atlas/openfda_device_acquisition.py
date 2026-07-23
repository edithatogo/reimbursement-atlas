"""Deterministic acquisition of the complete openFDA device classification corpus."""

from __future__ import annotations

import hashlib
import json
import time
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Any, cast

BASE_URL = "https://api.fda.gov/device/classification.json"
PAGE_SIZE = 1000
FetchJson = Callable[[str], dict[str, Any]]


class OpenFdaAcquisitionError(ValueError):
    """Raised when the paginated openFDA response is incomplete or inconsistent."""


def acquire_complete_device_classifications(  # ruff:ignore[too-many-locals]
    *,
    fetch_json: FetchJson | None = None,
    page_size: int = PAGE_SIZE,
    pause_seconds: float = 0.0,
) -> tuple[dict[str, object], dict[str, object]]:
    """Fetch every current classification row and return payload plus audit summary."""
    fetch = fetch_json or _fetch_json
    if not 1 <= page_size <= PAGE_SIZE:
        message = f"page_size must be between 1 and {PAGE_SIZE}"
        raise OpenFdaAcquisitionError(message)
    rows: list[dict[str, Any]] = []
    expected_total: int | None = None
    page_checksums: list[str] = []
    skip = 0
    while expected_total is None or skip < expected_total:
        url = f"{BASE_URL}?{urllib.parse.urlencode({'limit': page_size, 'skip': skip})}"
        page = fetch(url)
        metadata = cast("dict[str, Any]", page.get("meta", {}))
        result_metadata = cast("dict[str, Any]", metadata.get("results", {}))
        page_rows = cast("list[dict[str, Any]]", page.get("results", []))
        total = int(result_metadata.get("total", 0))
        observed_skip = int(result_metadata.get("skip", -1))
        if total <= 0 or observed_skip != skip or not page_rows:
            message = f"invalid openFDA page metadata at skip={skip}"
            raise OpenFdaAcquisitionError(message)
        if expected_total is None:
            expected_total = total
        elif total != expected_total:
            message = f"openFDA total changed during acquisition: {expected_total} -> {total}"
            raise OpenFdaAcquisitionError(message)
        page_checksums.append(
            hashlib.sha256(
                json.dumps(page_rows, separators=(",", ":"), sort_keys=True).encode()
            ).hexdigest()
        )
        rows.extend(page_rows)
        skip += len(page_rows)
        if pause_seconds:
            time.sleep(pause_seconds)
    if len(rows) != expected_total:
        message = f"incomplete openFDA corpus: expected={expected_total}, observed={len(rows)}"
        raise OpenFdaAcquisitionError(message)
    product_codes = [str(row.get("product_code", "")).strip() for row in rows]
    if not all(product_codes) or len(product_codes) != len(set(product_codes)):
        message = "openFDA corpus contains missing or duplicate product codes"
        raise OpenFdaAcquisitionError(message)
    rows.sort(key=lambda row: str(row["product_code"]))
    payload: dict[str, object] = {
        "meta": {
            "results": {
                "skip": 0,
                "limit": len(rows),
                "total": expected_total,
            }
        },
        "results": rows,
    }
    summary: dict[str, object] = {
        "schema_version": "openfda-device-acquisition-v1",
        "status": "complete",
        "source_url": BASE_URL,
        "page_size": page_size,
        "page_count": len(page_checksums),
        "record_count": len(rows),
        "unique_product_codes": len(set(product_codes)),
        "page_sha256": page_checksums,
        "payload_sha256": hashlib.sha256(
            (json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n").encode()
        ).hexdigest(),
    }
    return payload, summary


def _fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(  # ruff:ignore[suspicious-url-open-usage] - fixed HTTPS provider endpoint
        url,
        headers={"User-Agent": "reimbursement-atlas/0.1 source-acquisition"},
    )
    # The request URL is constructed from the fixed HTTPS openFDA endpoint.
    with urllib.request.urlopen(request, timeout=60) as response:  # nosec B310  # ruff:ignore[suspicious-url-open-usage]
        return cast("dict[str, Any]", json.load(response))

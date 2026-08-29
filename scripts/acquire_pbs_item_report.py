"""Acquire the CC BY Services Australia PBS Item Report with governed receipts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import urllib.request
import zipfile
from operator import itemgetter
from pathlib import Path
from typing import Any, TypedDict, cast
from urllib.parse import urlparse

from reimburse_atlas.registry import project_root

PACKAGE_ID = "14b536d4-eb6a-485d-bf87-2e6e77ddbac1"
PACKAGE_API = f"https://data.gov.au/data/api/3/action/package_show?id={PACKAGE_ID}"
MAGDA_RECORD = f"https://dev.magda.io/dataset/ds-dga-{PACKAGE_ID}/details?q="
EXPECTED_LICENCE = "Creative Commons Attribution 3.0 Australia"
EXPECTED_CSV_COLUMNS = {
    "Benefits ($)",
    "Item_number",
    "Month",
    "Patient_Category",
    "Scheme",
    "Services",
    "State",
    "Year",
}
RAW_DIR = project_root() / "data/raw_live/au_pbs_item_report"
OUTPUT_DIR = project_root() / "data/derived/historical_sources/pbs_item_report_v1"


class ItemReportAcquisitionError(ValueError):
    """Raised when authoritative PBS Item Report metadata or bytes fail closed."""


class ResourceRow(TypedDict):
    """Normalized public catalogue resource."""

    format: str
    id: str
    last_modified: object
    name: str
    source_url: str


class ReceiptRow(ResourceRow):
    """Path-free receipt for a locally validated resource."""

    byte_size: int
    checksum_sha256: str
    licence: str
    raw_storage: str
    signature_valid: bool
    status: str


def _read_url(url: str) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {"data.gov.au", "www.data.gov.au"}:
        message = f"Unapproved PBS Item Report host: {parsed.hostname}"
        raise ItemReportAcquisitionError(message)
    request = urllib.request.Request(  # ruff: ignore[suspicious-url-open-usage] - HTTPS host is allow-listed above
        url, headers={"User-Agent": "reimbursement-atlas-acquisition/1.0"}
    )
    with urllib.request.urlopen(  # ruff: ignore[suspicious-url-open-usage]  # nosec B310 - HTTPS host allow-listed above
        request, timeout=120
    ) as response:
        return response.read()


def normalize_package(payload: dict[str, Any]) -> tuple[dict[str, Any], list[ResourceRow]]:
    """Return deterministic package metadata and resource rows."""
    if payload.get("success") is not True or not isinstance(payload.get("result"), dict):
        message = "data.gov.au package response is not successful"
        raise ItemReportAcquisitionError(message)
    package: dict[str, Any] = payload["result"]
    if package.get("license_title") != EXPECTED_LICENCE:
        message = "PBS Item Report licence is absent or has changed"
        raise ItemReportAcquisitionError(message)
    resources: list[ResourceRow] = []
    resources_value = package.get("resources")
    if not isinstance(resources_value, list):
        message = "PBS Item Report resources are absent"
        raise ItemReportAcquisitionError(message)
    raw_resources = cast("list[object]", resources_value)
    for value in raw_resources:
        if not isinstance(value, dict):
            message = "PBS Item Report resource is malformed"
            raise ItemReportAcquisitionError(message)
        resource = cast("dict[str, object]", value)
        url = str(resource.get("url", ""))
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in {"data.gov.au", "www.data.gov.au"}:
            message = f"Unapproved resource URL: {url}"
            raise ItemReportAcquisitionError(message)
        resources.append({
            "format": str(resource.get("format", "")),
            "id": str(resource.get("id", "")),
            "last_modified": resource.get("last_modified"),
            "name": str(resource.get("name", "")),
            "source_url": url,
        })
    resources.sort(key=itemgetter("id"))
    summary = {
        "catalogue_record": MAGDA_RECORD,
        "coverage_note": (
            "Annual/YTD aggregate PBS and RPBS item services and benefits paid; "
            "not schedule pricing."
        ),
        "data_gov_package_api": PACKAGE_API,
        "dataset_id": PACKAGE_ID,
        "formats": sorted({row["format"] for row in resources}),
        "licence": EXPECTED_LICENCE,
        "metadata_modified": package.get("metadata_modified"),
        "resource_count": len(resources),
        "schema_version": "pbs-item-report-catalogue-v1",
        "temporal_coverage": "1992-2016 YTD",
        "title": package.get("title"),
    }
    return summary, resources


def _previous_receipts(path: Path) -> dict[str, dict[str, object]]:
    if not path.is_file():
        return {}
    rows: dict[str, dict[str, object]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        value: object = json.loads(line)
        if isinstance(value, dict):
            row = cast("dict[str, object]", value)
            resource_id = row.get("id")
            if isinstance(resource_id, str):
                rows[resource_id] = row
    return rows


def _catalogue_metadata_matches(resource: ResourceRow, previous: dict[str, object] | None) -> bool:
    if previous is None:
        return False
    keys = ("format", "id", "last_modified", "name", "source_url")
    return all(previous.get(key) == resource[key] for key in keys)


def _signature_valid(path: Path, suffix: str) -> bool:
    if suffix in {".zip", ".xlsx"}:
        return zipfile.is_zipfile(path)
    if suffix != ".csv":
        return False
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            header = next(csv.reader(handle))
    except OSError, UnicodeDecodeError, StopIteration, csv.Error:
        return False
    return set(header) == EXPECTED_CSV_COLUMNS


def acquire(
    resources: list[ResourceRow],
    *,
    raw_dir: Path = RAW_DIR,
    previous_receipts_path: Path = OUTPUT_DIR / "resources.jsonl",
) -> list[ReceiptRow]:
    """Download resources to ignored storage and return path-free receipts."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    previous = _previous_receipts(previous_receipts_path)
    receipts: list[ReceiptRow] = []
    for resource in resources:
        suffix = Path(urlparse(resource["source_url"]).path).suffix.lower() or ".bin"
        path = raw_dir / f"{resource['id']}{suffix}"
        status = "cached"
        cache_matches = _catalogue_metadata_matches(resource, previous.get(resource["id"]))
        existed = path.is_file() and path.stat().st_size > 0
        if not path.is_file() or path.stat().st_size == 0 or not cache_matches:
            data = _read_url(resource["source_url"])
            path.write_bytes(data)
            status = "refreshed" if existed else "downloaded"
        digest_builder = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest_builder.update(chunk)
        signature_valid = _signature_valid(path, suffix)
        if not signature_valid:
            message = f"Invalid {resource['format']} signature for {resource['id']}"
            raise ItemReportAcquisitionError(message)
        receipts.append({
            **resource,
            "byte_size": path.stat().st_size,
            "checksum_sha256": digest_builder.hexdigest(),
            "licence": EXPECTED_LICENCE,
            "raw_storage": "ignored_local_only",
            "signature_valid": True,
            "status": f"{status}_validated",
        })
    return receipts


def write_outputs(summary: dict[str, Any], rows: list[ResourceRow] | list[ReceiptRow]) -> None:
    """Write deterministic public catalogue metadata and acquisition receipts."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (OUTPUT_DIR / "resources.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    fields = sorted({key for row in rows for key in row})
    with (OUTPUT_DIR / "resources.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Fetch current metadata and optionally acquire all resource payloads."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    payload = json.loads(_read_url(PACKAGE_API))
    summary, resources = normalize_package(payload)
    rows = acquire(resources) if args.download else resources
    write_outputs(summary, rows)
    print(json.dumps({"downloaded": args.download, "resource_count": len(rows)}))


if __name__ == "__main__":
    main()

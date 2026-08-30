"""Verify historical PBS receipts against independent archive observations."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
from collections import defaultdict
from datetime import UTC, datetime
from operator import itemgetter
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

from reimburse_atlas.licence_review import pbs_raw_redistribution_status
from reimburse_atlas.registry import project_root

OUTPUT = project_root() / "data/derived/historical_sources/pbs_archive_verification_v1"
TARGETS = project_root() / "data/seed/historical_pbs_archive_targets.jsonl"
RECEIPTS = (
    project_root()
    / "data/derived/historical_sources/pbs_archive_v1/historical_source_downloads.jsonl"
)
CDX_ENDPOINT = "https://web.archive.org/cdx/search/cdx"
PBS_PUBLICATION_PREFIX = "https://www.pbs.gov.au/publication/schedule/"
PBS_COPYRIGHT_URL = "https://www.pbs.gov.au/info/general/copyright"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a JSON Lines object stream."""
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def canonical_url(value: str) -> str:
    """Remove transport-only query and fragment components for archive matching."""
    parsed = urlparse(value)
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, "", "", ""))


def archive_identity_url(value: str) -> str:
    """Normalize transport-only scheme differences for archive identity joins."""
    parsed = urlparse(canonical_url(value))
    return urlunparse(("https", parsed.netloc, parsed.path, "", "", ""))


def _sha1_base32(path: Path) -> str:
    digest = hashlib.sha1(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return base64.b32encode(digest.digest()).decode("ascii").rstrip("=")


def parse_cdx_payload(payload: Any) -> list[dict[str, str]]:
    """Normalize a CDX JSON table while rejecting malformed rows."""
    if not isinstance(payload, list) or not payload or not isinstance(payload[0], list):
        return []
    table = cast("list[Any]", payload)
    fields = [str(value) for value in cast("list[Any]", table[0])]
    rows: list[dict[str, str]] = []
    for raw_values in table[1:]:
        values = cast("list[Any]", raw_values) if isinstance(raw_values, list) else []
        if len(values) != len(fields):
            continue
        rows.append(dict(zip(fields, (str(value) for value in values), strict=True)))
    return rows


def _fetch_cdx(prefix: str) -> list[dict[str, str]]:
    params = urlencode(
        {
            "url": f"{prefix}*",
            "output": "json",
            "fl": "timestamp,original,statuscode,mimetype,digest,length",
            "filter": ["statuscode:200", "mimetype:application/pdf"],
            "collapse": "digest",
        },
        doseq=True,
    )
    request = Request(  # ruff:ignore[suspicious-url-open-usage] - fixed Internet Archive host
        f"{CDX_ENDPOINT}?{params}",
        headers={"User-Agent": "reimbursement-atlas-verification/1.0"},
    )
    with urlopen(request, timeout=120) as response:  # nosec B310  # ruff:ignore[suspicious-url-open-usage]
        return parse_cdx_payload(json.loads(response.read().decode("utf-8")))


def archive_prefix(value: str) -> str:
    """Bound CDX queries to one official annual archive subtree."""
    parsed = urlparse(canonical_url(value))
    parts = parsed.path.strip("/").split("/")
    try:
        schedule_index = parts.index("schedule")
        bounded_parts = parts[: schedule_index + 2]
    except ValueError, IndexError:
        bounded_parts = parts[:-1]
    path = "/".join(bounded_parts)
    return f"{parsed.scheme}://{parsed.netloc}/{path}/"


def refresh_cdx(targets: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Fetch one collapsed CDX inventory for the official PBS publication subtree."""
    del targets  # The bounded official prefix covers every target without per-file requests.
    captures: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in _fetch_cdx(PBS_PUBLICATION_PREFIX):
        key = (canonical_url(row["original"]), row["digest"], row["timestamp"])
        captures[key] = row
    return [captures[key] for key in sorted(captures)]


def build_verification_rows(  # ruff:ignore[too-many-locals] - explicit evidence comparison state
    targets: list[dict[str, Any]],
    receipts: list[dict[str, Any]],
    captures: list[dict[str, str]],
    *,
    previous_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Build checksum-aware verification rows without overstating weak observations."""
    receipt_by_id = {str(row["id"]): row for row in receipts}
    previous_by_id = {str(row["id"]): row for row in previous_rows or []}
    captures_by_url: dict[str, list[dict[str, str]]] = defaultdict(list)
    for capture in captures:
        captures_by_url[archive_identity_url(capture["original"])].append(capture)

    rows: list[dict[str, Any]] = []
    root = project_root()
    for target in sorted(targets, key=lambda row: str(row["id"])):
        identifier = str(target["id"])
        receipt = receipt_by_id.get(identifier, {})
        source_url = canonical_url(str(target["file_url"]))
        matching_captures = sorted(
            captures_by_url.get(archive_identity_url(source_url), []),
            key=itemgetter("timestamp", "digest"),
        )
        sha256 = receipt.get("checksum_sha256")
        sha1_base32: str | None = None
        cache_path_value = receipt.get("cache_path")
        if isinstance(cache_path_value, str) and cache_path_value:
            cache_path = Path(cache_path_value)
            if not cache_path.is_absolute():
                cache_path = root / cache_path
            if cache_path.is_file():
                sha1_base32 = _sha1_base32(cache_path)
        previous = previous_by_id.get(identifier, {})
        if (
            sha1_base32 is None
            and sha256
            and previous.get("local_checksum_sha256") == sha256
            and isinstance(previous.get("local_checksum_sha1_base32"), str)
        ):
            sha1_base32 = str(previous["local_checksum_sha1_base32"])

        archive_digests = sorted({capture["digest"] for capture in matching_captures})
        if sha1_base32 and sha1_base32 in archive_digests:
            status = "exact_digest_match"
        elif sha1_base32 and archive_digests:
            status = "digest_mismatch"
        elif archive_digests:
            status = "archive_capture_unverified"
        else:
            status = "no_archive_capture"
        rows.append({
            "id": identifier,
            "source_version_id": target["source_version_id"],
            "source_url": source_url,
            "official_receipt_status": receipt.get("status", "missing"),
            "local_checksum_sha256": sha256,
            "local_checksum_sha1_base32": sha1_base32,
            "archive_capture_count": len(matching_captures),
            "archive_digests_sha1_base32": archive_digests,
            "archive_timestamps": sorted({row["timestamp"] for row in matching_captures}),
            "verification_status": status,
            "source_byte_verified": status == "exact_digest_match",
            "publication_identity_observed": True,
            "raw_redistribution_status": pbs_raw_redistribution_status(source_url),
            "rights_source": PBS_COPYRIGHT_URL,
        })
    return rows


def _write_jsonl_csv(rows: list[dict[str, Any]], stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    stem.with_suffix(".jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    fields = sorted({key for row in rows for key in row})
    with stem.with_suffix(".csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(
            {
                key: json.dumps(value) if isinstance(value, list) else value
                for key, value in row.items()
            }
            for row in rows
        )


def write_outputs(
    rows: list[dict[str, Any]], captures: list[dict[str, str]], *, observed_at: str | None = None
) -> None:
    """Write public verification evidence and a fail-closed rights summary."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    _write_jsonl_csv(rows, OUTPUT / "pbs_archive_verification")
    capture_path = OUTPUT / "internet_archive_cdx_observations.jsonl"
    capture_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in captures), encoding="utf-8"
    )
    status_counts: dict[str, int] = {}
    for row in rows:
        status = str(row["verification_status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    summary = {
        "schema_version": "pbs-archive-verification-v1",
        "target_count": len(rows),
        "internet_archive_capture_count": len(captures),
        "verification_status_counts": status_counts,
        "observed_at": observed_at,
        "december_1987_source_byte_status": next(
            (
                row["verification_status"]
                for row in rows
                if "1987_12_01" in str(row["source_version_id"])
            ),
            "not_in_inventory",
        ),
        "raw_publication_status": "not_published_by_this_metadata_product",
        "raw_redistribution_status": pbs_raw_redistribution_status(PBS_COPYRIGHT_URL),
        "permission_record": "data/licence_review/pbs_raw_permission.json",
        "public_product_scope": "checksums_provenance_archive_observations_and_permitted_metadata",
        "copyright_url": PBS_COPYRIGHT_URL,
        "claim_boundary": (
            "Archive metadata and indexed text verify publication identity only. Exact source-byte "
            "verification requires a matching digest; local acquisition does not grant "
            "redistribution rights."
        ),
    }
    (OUTPUT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    """Refresh external observations when requested, then regenerate verification outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-cdx", action="store_true")
    args = parser.parse_args()
    targets = load_jsonl(TARGETS)
    receipts = load_jsonl(RECEIPTS)
    capture_path = OUTPUT / "internet_archive_cdx_observations.jsonl"
    previous_path = OUTPUT / "pbs_archive_verification.jsonl"
    observed_at: str | None = None
    if args.refresh_cdx:
        captures = refresh_cdx(targets)
        observed_at = datetime.now(tz=UTC).isoformat()
    else:
        captures = load_jsonl(capture_path)
        summary_path = OUTPUT / "summary.json"
        if summary_path.exists():
            observed_at = json.loads(summary_path.read_text(encoding="utf-8")).get("observed_at")
    rows = build_verification_rows(
        targets, receipts, captures, previous_rows=load_jsonl(previous_path)
    )
    write_outputs(rows, captures, observed_at=observed_at)
    print(json.dumps({"targets": len(rows), "captures": len(captures), "output": str(OUTPUT)}))


if __name__ == "__main__":
    main()

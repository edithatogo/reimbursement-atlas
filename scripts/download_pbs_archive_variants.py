"""Preserve differing Internet Archive PBS variants in ignored local storage."""

from __future__ import annotations

import base64
import csv
import hashlib
import json
import subprocess  # nosec B404 - fixed curl argv and fixed archive host
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

from reimburse_atlas.licence_review import pbs_raw_redistribution_status
from reimburse_atlas.registry import project_root

OUTPUT = project_root() / "data/derived/historical_sources/pbs_archive_verification_v1"
RAW = project_root() / "data/raw_live/historical_sources/pbs_internet_archive_variants"


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
    """Normalize HTTP and HTTPS captures to one source identity."""
    parsed = urlparse(canonical_url(value))
    return urlunparse(("https", parsed.netloc, parsed.path, "", "", ""))


def replay_url(timestamp: str, original: str) -> str:
    """Return a byte-preserving Wayback replay URL."""
    return f"https://web.archive.org/web/{timestamp}id_/{canonical_url(original)}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha1_base32(path: Path) -> str:
    """Return the base32 SHA-1 representation used by Internet Archive CDX."""
    digest = hashlib.sha1(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return base64.b32encode(digest.digest()).decode("ascii").rstrip("=")


def download_variant(url: str, destination: Path) -> tuple[str, str]:
    """Download one archive replay without accepting HTML error pages."""
    if not url.startswith("https://web.archive.org/web/"):
        return "blocked_untrusted_host", "Replay URL is not on the fixed Internet Archive host."
    if destination.exists():
        return "cached", "Existing ignored archive variant retained."
    destination.parent.mkdir(parents=True, exist_ok=True)
    incoming = destination.with_name(f".{destination.name}.incoming")
    incoming.unlink(missing_ok=True)
    command = [
        "curl",
        "--fail",
        "--silent",
        "--show-error",
        "--location",
        "--proto",
        "=https",
        "--tlsv1.2",
        "--retry",
        "2",
        "--connect-timeout",
        "20",
        "--max-time",
        "180",
        "--output",
        str(incoming),
        url,
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)  # nosec B603
    except (OSError, subprocess.CalledProcessError) as exc:
        incoming.unlink(missing_ok=True)
        detail = getattr(exc, "stderr", "") or str(exc)
        return "download_failed", detail.strip()[-500:]
    if not incoming.is_file():
        return "download_failed", "Archive replay completed without producing an output file."
    if not incoming.read_bytes()[:8].startswith(b"%PDF-"):
        incoming.unlink(missing_ok=True)
        return "invalid_content", "Archive replay did not return a PDF payload."
    incoming.replace(destination)
    return "downloaded", "Archived variant preserved in ignored local storage."


def plan_variants(
    verification_rows: list[dict[str, Any]], captures: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Plan only captures whose digest differs from the current official bytes."""
    mismatches = {
        archive_identity_url(str(row["source_url"])): row
        for row in verification_rows
        if row.get("verification_status") == "digest_mismatch"
    }
    planned: list[dict[str, Any]] = []
    for capture in captures:
        capture_url = canonical_url(str(capture["original"]))
        verification = mismatches.get(archive_identity_url(capture_url))
        if verification is None:
            continue
        timestamp = str(capture["timestamp"])
        digest = str(capture["digest"])
        planned.append({
            "id": f"{verification['id']}_{timestamp}_{digest}",
            "source_id": verification["id"],
            "official_source_url": canonical_url(str(verification["source_url"])),
            "archive_replay_url": replay_url(timestamp, capture_url),
            "archive_timestamp": timestamp,
            "archive_checksum_sha1_base32": digest,
            "raw_redistribution_status": pbs_raw_redistribution_status(
                str(verification["source_url"])
            ),
        })
    return sorted(planned, key=lambda row: str(row["id"]))


def write(rows: list[dict[str, Any]]) -> None:
    """Write checksum receipts for ignored archived variants."""
    path = OUTPUT / "internet_archive_variant_receipts.jsonl"
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    fields = sorted({key for row in rows for key in row})
    with path.with_suffix(".csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    summary = {
        "schema_version": "pbs-internet-archive-variant-receipts-v1",
        "variant_count": len(rows),
        "status_counts": counts,
        "raw_cache_policy": "ignored_local_only",
        "publication_effect": "none",
        "claim_boundary": (
            "A differing archive digest establishes a historical byte variant, not which variant "
            "is substantively correct and not permission to redistribute either payload."
        ),
    }
    (OUTPUT / "internet_archive_variant_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    """Download differing archive captures and record immutable checksums."""
    verification = load_jsonl(OUTPUT / "pbs_archive_verification.jsonl")
    captures = load_jsonl(OUTPUT / "internet_archive_cdx_observations.jsonl")
    rows = plan_variants(verification, captures)
    for row in rows:
        destination = RAW / f"{row['id']}.pdf"
        status, detail = download_variant(str(row["archive_replay_url"]), destination)
        row["status"] = status
        row["detail"] = detail
        if destination.exists() and status in {"downloaded", "cached"}:
            row["byte_size"] = destination.stat().st_size
            row["checksum_sha256"] = _sha256(destination)
            observed_sha1 = sha1_base32(destination)
            row["checksum_sha1_base32"] = observed_sha1
            row["archive_digest_verified"] = observed_sha1 == row["archive_checksum_sha1_base32"]
            if not row["archive_digest_verified"]:
                row["status"] = "archive_digest_mismatch"
                row["detail"] = "Downloaded replay bytes do not match the CDX digest."
        else:
            row["byte_size"] = None
            row["checksum_sha256"] = None
            row["checksum_sha1_base32"] = None
            row["archive_digest_verified"] = False
    write(rows)
    print(json.dumps({"variant_count": len(rows), "output": str(OUTPUT)}))


if __name__ == "__main__":
    main()

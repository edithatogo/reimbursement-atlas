"""Discover official historical machine-readable PBS publication packages."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from reimburse_atlas.registry import project_root

HISTORICAL_PAGE = "https://www.pbs.gov.au/info/publication/schedule/historical-archive"
OUTPUT = project_root() / "data/derived/historical_sources/pbs_structured_archive_v1"
SEED = project_root() / "data/seed/historical_pbs_structured_archive_targets.jsonl"
SUPPORTED_SUFFIXES = {".zip", ".csv", ".xml", ".txt"}


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a" and (href := dict(attrs).get("href")):
            self.links.append(href)


def fetch_links(url: str) -> list[str]:
    """Return canonical links from a fixed official PBS archive page."""
    request = Request(  # ruff:ignore[suspicious-url-open-usage] - fixed official HTTPS pages
        url, headers={"User-Agent": "reimbursement-atlas-archive/1.0"}
    )
    with urlopen(request, timeout=90) as response:  # nosec B310  # ruff:ignore[suspicious-url-open-usage]
        parser = _LinkParser()
        parser.feed(response.read().decode("utf-8", errors="replace"))
    return sorted({urljoin(url, href) for href in parser.links})


def classify_format(file_name: str) -> str | None:
    """Classify package semantics conservatively from the official filename."""
    name = file_name.lower()
    suffix = Path(name).suffix.lstrip(".")
    if "csv" in name:
        return "csv_zip" if suffix == "zip" else "csv"
    if "xml" in name or any(
        marker in name for marker in ("v2-down-converted", "v3extracts", "v3soextracts")
    ):
        return "xml_zip" if suffix == "zip" else "xml"
    if any(marker in name for marker in ("ascii", "text", "txt")):
        return "text_zip" if suffix == "zip" else "text"
    if "extracts" in name:
        return "structured_extract_zip" if suffix == "zip" else "structured_extract"
    if suffix in {"csv", "xml", "txt"}:
        return suffix
    return None


def discover(year: int | None = None) -> list[dict[str, object]]:
    """Discover official structured packages separately from publication PDFs."""
    current_year = year or datetime.now(tz=UTC).year
    pages = [
        HISTORICAL_PAGE,
        *(
            f"https://www.pbs.gov.au/info/publication/schedule/{y}"
            for y in range(2003, current_year + 1)
        ),
    ]
    rows: dict[str, dict[str, object]] = {}
    for page in pages:
        for url in fetch_links(page):
            parsed = urlparse(url)
            suffix = Path(parsed.path).suffix.lower()
            if parsed.scheme != "https" or parsed.netloc != "www.pbs.gov.au":
                continue
            if suffix not in SUPPORTED_SUFFIXES:
                continue
            canonical_url = parsed._replace(fragment="").geturl()
            digest = hashlib.sha256(canonical_url.encode()).hexdigest()
            file_name = Path(parsed.path).name
            date_match = re.search(r"(?:19|20)\d{2}-\d{2}-\d{2}", file_name)
            period = date_match.group(0) if date_match else "unknown"
            structured_format = classify_format(file_name)
            if structured_format is None:
                continue
            identifier = f"au_pbs_structured_{digest[:16]}"
            rows[identifier] = {
                "archive_page": page,
                "archive_period": period,
                "download_policy": "download_for_local_review",
                "file_kind": suffix.lstrip("."),
                "file_name": file_name,
                "file_url": canonical_url,
                "id": identifier,
                "licence_gate": "public_reuse_review",
                "notes": (
                    "Official machine-readable PBS publication package. Format and checksum "
                    "evidence do not by themselves grant redistribution rights or establish "
                    "cross-version field parity."
                ),
                "source_id": "au_pbs",
                "source_version_id": (
                    f"au_pbs_structured_{period.replace('-', '_')}_{digest[:12]}"
                ),
                "status": "planned",
                "structured_format": structured_format,
                "structured_api_equivalence": False,
            }
    return sorted(rows.values(), key=lambda row: str(row["id"]))


def write(rows: list[dict[str, object]]) -> None:
    """Write deterministic structured-source targets and format coverage."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    SEED.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    SEED.write_text(payload, encoding="utf-8")
    (OUTPUT / "historical_pbs_structured_targets.jsonl").write_text(payload, encoding="utf-8")
    fields = sorted({key for row in rows for key in row})
    with (OUTPUT / "historical_pbs_structured_targets.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    format_counts: dict[str, int] = {}
    for row in rows:
        value = str(row["structured_format"])
        format_counts[value] = format_counts.get(value, 0) + 1
    periods = sorted(
        str(row["archive_period"]) for row in rows if row["archive_period"] != "unknown"
    )
    summary = {
        "schema_version": "historical-pbs-structured-targets-v1",
        "target_count": len(rows),
        "period_start": periods[0] if periods else None,
        "period_end": periods[-1] if periods else None,
        "format_counts": format_counts,
        "raw_cache_policy": "ignored_local_only",
        "publication_effect": "none",
        "structured_api_equivalence": False,
        "licence_policy": "download_does_not_grant_redistribution_rights",
    }
    (OUTPUT / "targets_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    """Discover and write the official structured-download inventory."""
    rows = discover()
    write(rows)
    print(json.dumps({"target_count": len(rows), "output": str(OUTPUT)}))


if __name__ == "__main__":
    main()

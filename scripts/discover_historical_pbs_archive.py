"""Discover official historical PBS schedule PDFs without storing payloads."""

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

ARCHIVE_ROOT = "https://www.pbs.gov.au/info/publication/schedule/archive"
HISTORICAL_PAGE = "https://www.pbs.gov.au/info/publication/schedule/historical-archive"
OUTPUT = project_root() / "data/derived/historical_sources/pbs_archive_v1"
SEED = project_root() / "data/seed/historical_pbs_archive_targets.jsonl"


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a" and (href := dict(attrs).get("href")):
            self.links.append(href)


def fetch_links(url: str) -> list[str]:
    """Return canonical links from an official PBS archive page."""
    request = Request(  # ruff:ignore[suspicious-url-open-usage] - fixed official HTTPS pages
        url, headers={"User-Agent": "reimbursement-atlas-archive/1.0"}
    )
    with urlopen(request, timeout=90) as response:  # nosec B310  # ruff:ignore[suspicious-url-open-usage]
        parser = _LinkParser()
        parser.feed(response.read().decode("utf-8", errors="replace"))
    return sorted({urljoin(url, href) for href in parser.links})


def discover(year: int | None = None) -> list[dict[str, object]]:
    """Discover schedule PDFs from 1951 through the current archive year."""
    current_year = year or datetime.now(tz=UTC).year
    pages = [
        HISTORICAL_PAGE,
        *(
            f"https://www.pbs.gov.au/info/publication/schedule/{y}"
            for y in range(2003, current_year + 1)
        ),
    ]
    rows: list[dict[str, object]] = []
    for page in pages:
        for url in fetch_links(page):
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.netloc != "www.pbs.gov.au":
                continue
            if not parsed.path.lower().endswith(".pdf"):
                continue
            canonical_url = parsed._replace(fragment="").geturl()
            digest = hashlib.sha256(canonical_url.encode()).hexdigest()
            file_name = Path(parsed.path).name
            date_match = re.search(r"(?:19|20)\d{2}-\d{2}-\d{2}", file_name)
            period = date_match.group(0) if date_match else "unknown"
            period_id = period.replace("-", "_")
            rows.append({
                "archive_page": page,
                "archive_period": period,
                "download_policy": "download_for_local_review",
                "file_kind": "pdf",
                "file_name": file_name,
                "file_url": canonical_url,
                "id": f"au_pbs_archive_{digest[:16]}",
                "licence_gate": "public_reuse_review",
                "notes": (
                    "Official PBS Schedule publication PDF. Suitable for checksum-bound "
                    "historical citation; not equivalent to a structured API snapshot."
                ),
                "source_id": "au_pbs",
                "source_version_id": f"au_pbs_archive_{period_id}_{digest[:12]}",
                "status": "planned",
            })
    return sorted({str(row["id"]): row for row in rows}.values(), key=lambda row: str(row["id"]))


def write(rows: list[dict[str, object]]) -> None:
    """Write deterministic metadata inventory and summary."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    SEED.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    SEED.write_text(payload, encoding="utf-8")
    (OUTPUT / "historical_pbs_archive_targets.jsonl").write_text(payload, encoding="utf-8")
    fields = sorted({key for row in rows for key in row})
    with (OUTPUT / "historical_pbs_archive_targets.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    known_periods = sorted(
        str(row["archive_period"]) for row in rows if row["archive_period"] != "unknown"
    )
    summary = {
        "schema_version": "historical-pbs-archive-targets-v1",
        "target_count": len(rows),
        "period_start": known_periods[0] if known_periods else None,
        "period_end": known_periods[-1] if known_periods else None,
        "unknown_period_count": sum(row["archive_period"] == "unknown" for row in rows),
        "payload_format": "official_publication_pdf",
        "structured_api_equivalence": False,
        "raw_cache_policy": "ignored_local_only",
        "publication_effect": "none",
    }
    (OUTPUT / "targets_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    """Discover and write the deterministic official publication inventory."""
    rows = discover()
    write(rows)
    print(json.dumps({"target_count": len(rows), "output": str(OUTPUT)}))


if __name__ == "__main__":
    main()

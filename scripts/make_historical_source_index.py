"""Build a metadata-only inventory of historical MBS archive targets."""

from __future__ import annotations

import argparse
import csv
import json
import operator
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen

from reimburse_atlas.registry import project_root

MBS_INDEX_URLS = (
    "https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/Content/MBSOnline-2010",
    "https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/Content/Prev-Downloads",
)
OFFICIAL_HOST = "www.mbsonline.gov.au"
FILE_SUFFIXES = (".csv", ".pdf", ".txt", ".xls", ".xlsx", ".zip")
ARCHIVE_MARKERS = ("downloads", "prev-downloads", "mbsonline-2010")


class _LinkParser(HTMLParser):
    """Extract href values without retaining source HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.links.append(href)


def _fetch(url: str) -> str:
    """Fetch one official HTML index with a bounded HTTPS timeout."""
    # The caller supplies only HTTPS URLs constrained by official_url().
    with urlopen(url, timeout=90) as response:  # noqa: S310  # nosec B310
        return response.read().decode("utf-8", errors="replace")


def official_url(base: str, href: str) -> str | None:
    """Resolve a link only when it remains on the official HTTPS host."""
    url = urljoin(base, href)
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != OFFICIAL_HOST:
        return None
    return url


def is_archive_page(url: str) -> bool:
    """Return whether a URL looks like an MBS archive index page."""
    path = urlparse(url).path.lower()
    return any(marker in path for marker in ARCHIVE_MARKERS)


def is_archive_file(url: str) -> bool:
    """Return whether a URL has a supported historical-file suffix."""
    return urlparse(url).path.lower().endswith(FILE_SUFFIXES)


def discover_targets() -> list[dict[str, str]]:
    """Discover archive pages and file links while keeping only metadata."""
    pages: list[str] = list(MBS_INDEX_URLS)
    seen_pages: set[str] = set()
    files: dict[str, dict[str, str]] = {}
    while pages and len(seen_pages) < 64:
        page = pages.pop(0)
        if page in seen_pages:
            continue
        seen_pages.add(page)
        parser = _LinkParser()
        parser.feed(_fetch(page))
        for href in parser.links:
            url = official_url(page, href)
            if url is None:
                continue
            if is_archive_file(url):
                files.setdefault(
                    url,
                    {
                        "archive_page": page,
                        "file_url": url,
                        "file_name": Path(urlparse(url).path).name,
                    },
                )
            elif is_archive_page(url) and url not in seen_pages:
                pages.append(url)

    rows: list[dict[str, str]] = []
    for index, row in enumerate(sorted(files.values(), key=operator.itemgetter("file_url")), 1):
        archive_path = urlparse(row["archive_page"]).path.rsplit("/", 1)[-1]
        row.update({
            "id": f"au_mbs_historical_{index:04d}",
            "source_id": "au_mbs",
            "source_version_id": f"au_mbs_historical_{index:04d}",
            "archive_page_id": archive_path,
            "archive_period": extract_period(row["file_name"]),
            "file_kind": Path(row["file_name"]).suffix.lower().lstrip("."),
            "licence_gate": "public_reuse_review",
            "download_policy": "manual_review_only",
            "status": "planned",
            "notes": (
                "Metadata-only historical target. Do not download, parse or publish "
                "without source-specific licence review."
            ),
        })
        rows.append(row)
    return rows


def extract_period(file_name: str) -> str:
    """Extract the first four-digit calendar year from a file name."""
    match = re.search(r"(?:19|20)\d{2}", Path(file_name).stem)
    if match:
        return match.group(0)
    return "unknown"


def _write_rows(rows: list[dict[str, str]], *, seed_path: Path, output_dir: Path) -> None:
    for row in rows:
        row["archive_period"] = extract_period(row["file_name"])
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    fields = sorted(rows[0]) if rows else ["id", "file_url"]
    with seed_path.open("w", encoding="utf-8", newline="") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    jsonl_path = output_dir / "historical_mbs_archive_targets.jsonl"
    jsonl_path.write_text(seed_path.read_text(encoding="utf-8"), encoding="utf-8")
    csv_path = output_dir / "historical_mbs_archive_targets.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "target_count": len(rows),
        "archive_page_count": len({row["archive_page"] for row in rows}),
        "periods": sorted({row["archive_period"] for row in rows}),
        "downloadable_targets": 0,
        "manual_review_targets": len(rows),
        "status": "metadata_only_review_required",
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    """Generate the historical MBS metadata seed and derived index."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Fetch official archive indexes and refresh the committed metadata seed.",
    )
    parser.add_argument(
        "--seed",
        type=Path,
        default=project_root() / "data/seed/historical_mbs_archive_targets.jsonl",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root() / "data/derived/historical_sources",
    )
    args = parser.parse_args()
    if args.refresh:
        rows = discover_targets()
    else:
        rows = [
            json.loads(line)
            for line in args.seed.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    _write_rows(rows, seed_path=args.seed, output_dir=args.output_dir)
    print(json.dumps({"target_count": len(rows), "output_dir": str(args.output_dir)}))


if __name__ == "__main__":
    main()

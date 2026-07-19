"""Discover official historical source files without storing source payloads."""

from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from operator import itemgetter
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen

from reimburse_atlas.registry import project_root

OUTPUT = project_root() / "data/derived/historical_sources/historical_source_catalog.jsonl"
CMS_PFS_INDEX = (
    "https://www.cms.gov/medicare/payment/fee-schedules/physician/national-payment-amount-file"
)
CMS_ASP_INDEX = "https://www.cms.gov/medicare/payment/part-b-drugs/asp-pricing-files"
NHS_GENOMICS_INDEX = "https://www.england.nhs.uk/publication/national-genomic-test-directories/"
PBS_LEGACY_PAGE = "https://data.pbs.gov.au/document/89997.html"
PUBLIC_HOSTS = {"www.cms.gov", "www.england.nhs.uk"}


class LinkParser(HTMLParser):
    """Collect href attributes from an official HTML page."""

    def __init__(self) -> None:
        """Initialise an empty link collector."""
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Record an anchor href when present."""
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value)


def fetch_links(url: str) -> list[str]:
    """Fetch one official page and return absolute links."""
    request = Request(  # noqa: S310 - URL is checked as HTTPS below
        url, headers={"User-Agent": "reimbursement-atlas-source-catalog/1.0"}
    )
    if urlparse(url).scheme != "https":
        return []
    with urlopen(request, timeout=30) as response:  # nosec B310  # noqa: S310
        parser = LinkParser()
        parser.feed(response.read().decode("utf-8", errors="replace"))
    return sorted({urljoin(url, link) for link in parser.links})


def file_kind(url: str) -> str:
    """Infer a conservative file kind from a URL."""
    suffix = Path(urlparse(url).path).suffix.lower().lstrip(".")
    return suffix or "download"


def target(*, source_id: str, page: str, url: str, gate: str, policy: str) -> dict[str, str]:
    """Create the common historical target record."""
    name = Path(urlparse(url).path).name or urlparse(url).netloc
    slug = re.sub(r"[^a-z0-9]+", "_", f"{source_id}_{name.lower()}").strip("_")
    slug = f"{slug}_{hashlib.sha256(url.encode()).hexdigest()[:10]}"
    return {
        "archive_page": page,
        "download_policy": policy,
        "file_kind": file_kind(url),
        "file_name": name,
        "file_url": url,
        "id": slug,
        "licence_gate": gate,
        "notes": (
            "Metadata discovered from the official archive page; download does not "
            "grant redistribution rights."
        ),
        "source_id": source_id,
        "source_version_id": slug,
        "status": "planned",
    }


def discover() -> list[dict[str, str]]:
    """Discover public and licence-gated historical targets."""
    rows: list[dict[str, str]] = []
    pfs_pages = [
        url
        for url in fetch_links(CMS_PFS_INDEX)
        if re.search(r"/pf(rev|all)\d", url, re.IGNORECASE)
    ]
    for page in pfs_pages:
        for url in fetch_links(page):
            if urlparse(url).netloc == "www.cms.gov" and urlparse(url).path.lower().endswith((
                ".zip",
                ".csv",
                ".txt",
            )):
                rows.append(
                    target(
                        source_id="us_cms_pfs",
                        page=page,
                        url=url,
                        gate="public_reuse_review",
                        policy="download_for_local_review",
                    )
                )
    for url in fetch_links(CMS_ASP_INDEX):
        parsed = urlparse(url)
        if parsed.netloc != "www.cms.gov" or not (
            parsed.path.lower().endswith(".zip")
            or ".zip" in parse_qs(parsed.query).get("file", [""])[0].lower()
        ):
            continue
        gated = "license" in url.lower() or "/apps/ama/" in url.lower()
        rows.append(
            target(
                source_id="us_cms_asp",
                page=CMS_ASP_INDEX,
                url=url,
                gate="restricted_or_licence_review" if gated else "public_reuse_review",
                policy="metadata_only_manual_review" if gated else "download_for_local_review",
            )
        )
    for url in fetch_links(NHS_GENOMICS_INDEX):
        parsed = urlparse(url)
        if parsed.netloc != "www.england.nhs.uk" or not parsed.path.lower().endswith((
            ".xlsx",
            ".xls",
            ".pdf",
        )):
            continue
        rows.append(
            target(
                source_id="uk_genomic_test_directory",
                page=NHS_GENOMICS_INDEX,
                url=url,
                gate="public_reuse_review",
                policy="download_for_local_review",
            )
        )
    rows.append({
        "archive_page": PBS_LEGACY_PAGE,
        "download_policy": "metadata_only_manual_review",
        "file_kind": "catalogue_page",
        "file_name": "PBS legacy historical distribution page",
        "file_url": PBS_LEGACY_PAGE,
        "id": "au_pbs_legacy_historical_catalogue",
        "licence_gate": "public_reuse_review",
        "notes": (
            "The legacy page exposes catalogue metadata but no stable historical "
            "payload link in this run; retain the page for later API/export review."
        ),
        "source_id": "au_pbs",
        "source_version_id": "au_pbs_legacy_historical_catalogue",
        "status": "planned",
    })
    return sorted({row["id"]: row for row in rows}.values(), key=itemgetter("id"))


def main() -> None:
    """Write the deterministic metadata-only catalog."""
    rows = discover()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    print(json.dumps({"output": str(OUTPUT), "target_count": len(rows)}))


if __name__ == "__main__":
    main()

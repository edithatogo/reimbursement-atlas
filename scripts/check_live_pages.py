"""Smoke-test the deployed GitHub Pages dashboard over HTTPS."""

from __future__ import annotations

import argparse
import time
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

EXPECTED_PATHS = (
    "favicon.svg",
    "status.json",
    "data/graph_nodes.csv",
    "data/graph_edges.csv",
)
DEFAULT_URL = "https://edithatogo.github.io/reimbursement-atlas/"
USER_AGENT = "reimbursement-atlas-live-pages-smoke/1"


class _FetchError(RuntimeError):
    """Identify a URL that remained unavailable after bounded retries."""

    def __init__(self, url: str, error: Exception | None) -> None:
        super().__init__(f"could not fetch {url}: {error}")


class _References(HTMLParser):
    """Collect URL-bearing references from the deployed HTML document."""

    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append(value)


def _fetch(url: str, attempts: int) -> tuple[int, bytes]:
    """Fetch a URL with bounded retries for Pages/CDN propagation."""
    request = Request(url, headers={"User-Agent": USER_AGENT})  # noqa: S310 - URL is validated below
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=20) as response:  # noqa: S310 - fixed HTTPS target
                return response.status, response.read()
        except (HTTPError, URLError, TimeoutError) as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(5)
    raise _FetchError(url, last_error) from last_error


def _same_origin(url: str, root: str) -> bool:
    """Return whether a URL belongs to the deployed dashboard origin."""
    return urlsplit(url).netloc == urlsplit(root).netloc


def validate_live_pages(root: str, attempts: int = 12) -> list[str]:
    """Return deployment errors for the public dashboard."""
    root = root.rstrip("/") + "/"
    root_parts = urlsplit(root)
    if root_parts.scheme != "https":
        return [f"live Pages URL must use HTTPS: {root}"]
    expected_prefix = root_parts.path
    status, body = _fetch(root, attempts)
    if status != 200:
        return [f"dashboard root returned HTTP {status}"]

    parser = _References()
    parser.feed(body.decode("utf-8"))
    errors: list[str] = []
    urls: set[str] = set()
    for reference in parser.references:
        if reference.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
            continue
        target = urljoin(root, reference)
        if not _same_origin(target, root):
            continue
        path = urlsplit(target).path
        if not path.startswith(expected_prefix):
            errors.append(f"root-relative or malformed dashboard reference: {reference}")
            continue
        urls.add(target)

    urls.update(urljoin(root, relative_path) for relative_path in EXPECTED_PATHS)
    for target in sorted(urls):
        target_status, _ = _fetch(target, attempts)
        if target_status != 200:
            errors.append(f"{target} returned HTTP {target_status}")
    return errors


def main() -> None:
    """Fail closed when the deployed dashboard has broken public references."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--attempts", type=int, default=12)
    args = parser.parse_args()
    errors = validate_live_pages(args.url, attempts=max(1, args.attempts))
    if errors:
        raise SystemExit("Live Pages smoke failed:\n- " + "\n- ".join(errors))
    print(f"Live Pages smoke passed: {args.url}")


if __name__ == "__main__":
    main()

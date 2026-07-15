"""Validate published dashboard routes and local navigation targets."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from reimburse_atlas.registry import project_root

EXPECTED_ROUTES = (
    "/",
    "/analyses/",
    "/automation/",
    "/crosswalks/",
    "/demonstrators/",
    "/ontologies/",
    "/readiness/",
    "/roadmap/",
    "/sources/",
)


class _Links(HTMLParser):
    """Collect local absolute links from a rendered page."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if href and href.startswith("/"):
            self.links.append(urlparse(href).path)


def _route_file(dist: Path, route: str) -> Path:
    """Map a static route to its generated HTML file."""
    return dist / ("index.html" if route == "/" else route.strip("/") + "/index.html")


def validate_dashboard_routes(dist: Path) -> list[str]:
    """Return missing route or local navigation errors."""
    errors: list[str] = []
    for route in EXPECTED_ROUTES:
        page = _route_file(dist, route)
        if not page.exists():
            errors.append(f"missing generated route: {route}")
            continue
        parser = _Links()
        parser.feed(page.read_text(encoding="utf-8"))
        for link in parser.links:
            if link.startswith("/data/") or link == "/status.json":
                target = dist / link.lstrip("/")
            elif link in EXPECTED_ROUTES:
                target = _route_file(dist, link)
            else:
                continue
            if not target.exists():
                errors.append(f"{route} links to missing target: {link}")
    return errors


def main() -> None:
    """Fail closed if the static dashboard contains broken public routes."""
    dist = project_root() / "apps" / "dashboard" / "dist"
    errors = validate_dashboard_routes(dist)
    if errors:
        raise SystemExit("Dashboard route check failed:\n- " + "\n- ".join(errors))
    print(f"Dashboard route check passed: {len(EXPECTED_ROUTES)} public routes are linked.")


if __name__ == "__main__":
    main()

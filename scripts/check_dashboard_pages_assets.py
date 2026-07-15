"""Validate asset and navigation prefixes for the GitHub Pages project site."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

from reimburse_atlas.registry import project_root, repo_relative

PAGES_BASE = "/reimbursement-atlas/"


class _References(HTMLParser):
    """Collect URL-bearing HTML attributes from generated pages."""

    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append(value)


def validate_pages_assets(dist: Path) -> list[str]:
    """Return project-site prefix violations in the generated static output."""
    errors: list[str] = []
    pages = sorted(dist.rglob("*.html"))
    if not pages:
        return [f"dashboard contains no HTML pages: {repo_relative(dist)}"]
    for page in pages:
        parser = _References()
        parser.feed(page.read_text(encoding="utf-8"))
        for reference in parser.references:
            if reference.startswith("/") and not reference.startswith(PAGES_BASE):
                errors.append(f"{repo_relative(page)} has root-relative Pages asset: {reference}")
    return errors


def main() -> None:
    """Fail closed when a Pages build would request assets from the domain root."""
    errors = validate_pages_assets(project_root() / "apps" / "dashboard" / "dist")
    if errors:
        raise SystemExit("GitHub Pages asset check failed:\n- " + "\n- ".join(errors))
    print("GitHub Pages asset check passed: generated references use the project-site prefix.")


if __name__ == "__main__":
    main()

"""Run deterministic accessibility and size checks against the static dashboard."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

from reimburse_atlas.registry import project_root, repo_relative


class _PageContract(HTMLParser):
    """Collect the minimum public-page accessibility contract."""

    def __init__(self) -> None:
        super().__init__()
        self.lang = False
        self.title = False
        self.viewport = False
        self.h1 = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "html" and attributes.get("lang"):
            self.lang = True
        elif tag == "title":
            self.title = True
        elif tag == "h1":
            self.h1 = True
        elif tag == "meta" and attributes.get("name") == "viewport":
            self.viewport = True


def validate_dashboard(dist: Path) -> list[str]:
    """Return contract violations for the generated static dashboard."""
    if not dist.is_dir():
        return [f"dashboard directory is missing: {repo_relative(dist)}"]
    pages = sorted(dist.rglob("*.html"))
    if not pages:
        return ["dashboard contains no HTML pages"]
    errors: list[str] = []
    for page in pages:
        parser = _PageContract()
        parser.feed(page.read_text(encoding="utf-8"))
        missing = [
            name
            for name, present in {
                "html lang": parser.lang,
                "title": parser.title,
                "viewport": parser.viewport,
                "h1": parser.h1,
            }.items()
            if not present
        ]
        if missing:
            errors.append(f"{repo_relative(page)} missing: {', '.join(missing)}")
        if page.stat().st_size > 1_000_000:
            errors.append(f"{repo_relative(page)} exceeds 1 MB page budget")
    status = dist / "status.json"
    if not status.exists():
        errors.append("dashboard status.json is missing")
    return errors


def main() -> None:
    """Validate the built dashboard and fail closed on violations."""
    errors = validate_dashboard(project_root() / "apps" / "dashboard" / "dist")
    if errors:
        raise SystemExit("Dashboard quality failed:\n- " + "\n- ".join(errors))
    print("Dashboard quality passed: accessibility contract and page budgets are valid.")


if __name__ == "__main__":
    main()

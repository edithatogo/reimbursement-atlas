"""Render GitHub issue drafts from the Conductor backlog.

The script intentionally writes markdown issue drafts rather than calling GitHub.
That keeps repository generation deterministic and avoids assuming credentials.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "conductor" / "backlog.yml"
OUTPUT = ROOT / ".github" / "generated-issues"


@dataclass
class IssueDraft:
    """Minimal issue data parsed from the constrained backlog YAML."""

    epic_id: str
    epic_title: str
    title: str
    labels: list[str] = field(default_factory=list)


def _strip_quotes(value: str) -> str:
    return value.strip().strip('"')


def parse_backlog(path: Path = BACKLOG) -> list[IssueDraft]:
    """Parse the simple Conductor backlog format into issue drafts."""
    issues: list[IssueDraft] = []
    epic_id = "UNKNOWN"
    epic_title = "Unknown epic"
    current: IssueDraft | None = None

    for line in path.read_text(encoding="utf-8").splitlines():
        if match := re.match(r"^  - id: (.+)$", line):
            epic_id = _strip_quotes(match.group(1))
            continue
        if match := re.match(r"^    title: (.+)$", line):
            epic_title = _strip_quotes(match.group(1))
            continue
        if match := re.match(r"^      - title: (.+)$", line):
            current = IssueDraft(
                epic_id=epic_id,
                epic_title=epic_title,
                title=_strip_quotes(match.group(1)),
            )
            issues.append(current)
            continue
        if current and (match := re.match(r"^        labels: (\[.+\])$", line)):
            parsed = ast.literal_eval(match.group(1))
            current.labels = [str(item) for item in parsed]
    return issues


def render_issue(issue: IssueDraft) -> str:
    """Render one GitHub issue draft."""
    labels = ", ".join(issue.labels) if issue.labels else "none"
    return f"""# {issue.title}

Epic: `{issue.epic_id}` — {issue.epic_title}

Labels: {labels}

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [ ] Scope is confirmed.
- [ ] Licence and data-governance implications are checked.
- [ ] Tests or validation evidence are defined.
- [ ] Documentation or Conductor context is updated.
"""


def slug(value: str) -> str:
    """Create a filesystem-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "issue"


def main() -> None:
    """Write issue drafts to `.github/generated-issues`."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for existing in OUTPUT.glob("*.md"):
        existing.unlink()
    count = 0
    for count, issue in enumerate(parse_backlog(), start=1):
        path = OUTPUT / f"{count:03d}-{slug(issue.title)}.md"
        path.write_text(render_issue(issue), encoding="utf-8")
    print(f"Wrote {count} issue drafts to {OUTPUT}")


if __name__ == "__main__":
    main()

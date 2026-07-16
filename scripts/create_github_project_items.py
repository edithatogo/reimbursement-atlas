"""Render GitHub issue drafts from the Conductor backlog.

The script intentionally writes markdown issue drafts rather than calling GitHub.
That keeps repository generation deterministic and avoids assuming credentials.
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

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
    parent_issue: str | None = None
    status: str | None = None


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


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            loaded = json.loads(line)
            if isinstance(loaded, dict):
                rows.append(cast("dict[str, object]", loaded))
    return rows


def generated_track_issues(
    root: Path = ROOT,
    *,
    parent_issue_titles: set[str] | None = None,
) -> list[IssueDraft]:
    """Generate issue drafts from machine-readable roadmap seed records."""
    seed_dir = root / "data" / "seed"
    tracks = {str(row["id"]): row for row in _read_jsonl(seed_dir / "conductor_tracks.jsonl")}
    issues: list[IssueDraft] = []
    for row in _read_jsonl(seed_dir / "roadmap_functions.jsonl"):
        track_id = str(row.get("track_id", "track_unknown"))
        track = tracks.get(track_id, {})
        issues.append(
            IssueDraft(
                epic_id=track_id.upper(),
                epic_title=str(track.get("title", "Conductor roadmap track")),
                title=str(row.get("github_issue_title", row.get("name", "Roadmap function"))),
                labels=[
                    "type:roadmap-function",
                    f"priority:{row.get('priority', 'unknown')}",
                    f"interface:{row.get('interface', 'unknown')}",
                    f"status:{row.get('status', 'planned')}",
                ],
                parent_issue=(
                    str(track.get("title"))
                    if str(track.get("title")) in (parent_issue_titles or set())
                    else None
                ),
                status=str(row.get("status", "planned")),
            )
        )
    for row in _read_jsonl(seed_dir / "dataset_candidates.jsonl"):
        issues.append(
            IssueDraft(
                epic_id="DATASET-CANDIDATES",
                epic_title="Additional dataset and country onboarding",
                title=f"Onboard dataset candidate: {row.get('name', row.get('id'))}",
                labels=[
                    "type:data-source",
                    f"priority:{row.get('priority', 'unknown')}",
                    "phase:future",
                ],
            )
        )
    for row in _read_jsonl(seed_dir / "research_questions.jsonl"):
        issues.append(
            IssueDraft(
                epic_id="RESEARCH-QUESTIONS",
                epic_title="Protocolled policy research questions",
                title=f"Complete protocol and report: {row.get('id')}",
                labels=["type:research", "type:osf", "phase:analysis"],
            )
        )
    for row in _read_jsonl(seed_dir / "output_artifact_plans.jsonl"):
        issues.append(
            IssueDraft(
                epic_id="OUTPUTS",
                epic_title="Publication and deployment outputs",
                title=f"Implement output plan: {row.get('id')}",
                labels=[
                    "type:publication",
                    f"target:{row.get('target_platform', 'unknown')}",
                ],
            )
        )
    return issues


def render_issue(issue: IssueDraft) -> str:
    """Render one GitHub issue draft."""
    labels = ", ".join(issue.labels) if issue.labels else "none"
    parent = f"Parent issue: {issue.parent_issue}\n\n" if issue.parent_issue else ""
    if issue.title == "Prototype Mojo fuzzy prefilter for large crosswalk candidate sets":
        acceptance = (
            "- [x] Scope is confirmed: candidate generation only, never an equivalence decision.\n"
            "- [x] Licence and data-governance implications are checked for the synthetic local "
            "fixture.\n"
            "- [x] Tests or validation evidence are defined: `pixi run fuzzy-benchmark` records "
            "recall,\n"
            "  precision and specificity at a deterministic threshold.\n"
            "- [x] Documentation or Conductor context is updated.\n"
            "- [ ] Human adjudication of real reviewed mappings is complete.\n\n"
            "Current synthetic fixture evidence: recall `1.0`, precision `1.0`, specificity `1.0 "
            "at\n"
            "threshold `0.2`. This does not establish evidence-grade performance."
        )
    elif issue.title == "Create signed release and Zenodo DOI after publication approval":
        acceptance = (
            "- [x] Scope is confirmed: prepare and validate metadata locally; do not deposit or "
            "mint a DOI.\n"
            "- [ ] Licence and data-governance implications are checked by an accountable human "
            "reviewer.\n"
            "- [x] Tests or validation evidence are defined: `pixi run zenodo-metadata` and "
            "focused unit tests.\n"
            "- [x] Documentation or Conductor context is updated; external deposition remains "
            "gated."
        )
    else:
        acceptance = """- [ ] Scope is confirmed.
- [ ] Licence and data-governance implications are checked.
- [ ] Tests or validation evidence are defined.
- [ ] Documentation or Conductor context is updated."""
    status_line = f"Status: `{issue.status}`\n\n" if issue.status else ""
    return f"""# {issue.title}

Epic: `{issue.epic_id}` — {issue.epic_title}

{parent}Labels: {labels}

{status_line}## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

{acceptance}
"""


def deduplicate_issues(issues: list[IssueDraft]) -> list[IssueDraft]:
    """Keep one generated draft when backlog and roadmap rows share a title."""
    unique: list[IssueDraft] = []
    seen_titles: set[str] = set()
    for issue in issues:
        key = issue.title.casefold()
        if key in seen_titles:
            continue
        seen_titles.add(key)
        unique.append(issue)
    return unique


def slug(value: str) -> str:
    """Create a filesystem-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "issue"


def existing_issue_paths(output: Path = OUTPUT) -> dict[str, list[Path]]:
    """Index existing drafts so adding a new issue does not renumber old ones."""
    paths: dict[str, list[Path]] = {}
    for path in output.glob("*.md"):
        match = re.match(r"^\d+-(.+)\.md$", path.name)
        if match:
            paths.setdefault(match.group(1), []).append(path)
    for path_list in paths.values():
        path_list.sort()
    return paths


def main() -> None:
    """Write issue drafts to `.github/generated-issues`."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    stable_paths = existing_issue_paths()
    used_numbers = {
        int(match.group(1))
        for path in OUTPUT.glob("*.md")
        if (match := re.match(r"^(\d+)-", path.name))
    }
    next_number = max(used_numbers, default=0) + 1
    for existing in OUTPUT.glob("*.md"):
        existing.unlink()
    backlog_issues = parse_backlog()
    parent_issue_titles = {issue.title for issue in backlog_issues}
    generated_issues = generated_track_issues(parent_issue_titles=parent_issue_titles)
    all_issues = deduplicate_issues([*backlog_issues, *generated_issues])
    for issue in all_issues:
        issue_slug = slug(issue.title)
        existing_paths = stable_paths.get(issue_slug, [])
        path = existing_paths.pop(0) if existing_paths else None
        if path is None:
            while next_number in used_numbers:
                next_number += 1
            path = OUTPUT / f"{next_number:03d}-{issue_slug}.md"
            used_numbers.add(next_number)
            next_number += 1
        path.write_text(render_issue(issue), encoding="utf-8")
    print(f"Wrote {len(all_issues)} issue drafts to {OUTPUT}")


if __name__ == "__main__":
    main()

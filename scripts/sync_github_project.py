"""Synchronise generated issue drafts into GitHub Projects without destructive writes."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess  # nosec B404 - the fixed GitHub CLI boundary is shell-free and argument-list based.
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root


def _run_gh(args: list[str], *, root: Path) -> Any:
    """Run a GitHub CLI command without exposing authentication material."""
    executable = shutil.which("gh")
    if executable is None:
        message = "GitHub CLI executable 'gh' was not found on PATH"
        raise RuntimeError(message)
    result = subprocess.run(  # nosec B603 - executable is resolved and shell execution is disabled.
        [executable, *args], cwd=root, check=False, capture_output=True, text=True
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown gh failure"
        message = f"gh {' '.join(args[:2])} failed: {detail}"
        raise RuntimeError(message)
    output = result.stdout.strip()
    if not output:
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        # ``gh issue create`` returns the issue URL as plain text, while list
        # and project commands return JSON.
        return output


def load_issue_drafts(path: Path) -> list[dict[str, Any]]:
    """Load issue-type rows from the generated Project JSONL export."""
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            continue
        row = cast("dict[str, Any]", value)
        if row.get("item_type") == "issue":
            rows.append(row)
    return rows


def _remote_issue_index(rows: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for value in cast("list[Any]", rows):
        if not isinstance(value, dict):
            continue
        row = cast("dict[str, Any]", value)
        if not isinstance(row.get("title"), str):
            continue
        indexed[str(row["title"])] = row
    return indexed


def project_numbers(rows: Any) -> set[str]:
    """Return issue numbers already present in a GitHub Project response."""
    if isinstance(rows, dict):
        rows = cast("dict[str, Any]", rows).get("items")
    if not isinstance(rows, list):
        return set()
    numbers: set[str] = set()
    for value in cast("list[Any]", rows):
        if not isinstance(value, dict):
            continue
        content = cast("dict[str, Any]", value).get("content")
        if not isinstance(content, dict):
            continue
        typed_content = cast("dict[str, Any]", content)
        if typed_content.get("number") is not None:
            numbers.add(str(typed_content["number"]))
    return numbers


def label_names(rows: Any) -> set[str]:
    """Return labels available for safe issue creation."""
    if not isinstance(rows, list):
        return set()
    names: set[str] = set()
    for value in cast("list[Any]", rows):
        if not isinstance(value, dict):
            continue
        name = cast("dict[str, Any]", value).get("name")
        if isinstance(name, str) and name:
            names.add(name)
    return names


def _issue_url(issue: dict[str, Any]) -> str | None:
    value = issue.get("url")
    return value if isinstance(value, str) and value else None


def sync_project(  # noqa: PLR0914 - keeps the read/plan/apply state explicit.
    *,
    root: Path,
    repository: str,
    owner: str,
    project_number: int,
    title_filters: tuple[str, ...] = (),
    apply: bool = False,
) -> list[dict[str, str]]:
    """Plan or apply idempotent issue and Project-item synchronisation."""
    export_path = root / "data" / "derived" / "github_project" / "github_project_items.jsonl"
    drafts = load_issue_drafts(export_path)
    if title_filters:
        drafts = [row for row in drafts if str(row.get("title")) in title_filters]
    remote_issues = _remote_issue_index(
        _run_gh(
            [
                "issue",
                "list",
                "--repo",
                repository,
                "--state",
                "all",
                "--limit",
                "1000",
                "--json",
                "title,url,number",
            ],
            root=root,
        )
    )
    project_items = project_numbers(
        _run_gh(
            [
                "project",
                "item-list",
                str(project_number),
                "--owner",
                owner,
                "--format",
                "json",
                "--limit",
                "1000",
            ],
            root=root,
        )
    )
    available_labels: set[str] = set()
    if apply:
        available_labels = label_names(
            _run_gh(
                [
                    "label",
                    "list",
                    "--repo",
                    repository,
                    "--limit",
                    "1000",
                    "--json",
                    "name",
                ],
                root=root,
            )
        )

    actions: list[dict[str, str]] = []
    for draft in drafts:
        title = str(draft.get("title", ""))
        issue = remote_issues.get(title)
        if issue is None:
            if not apply:
                actions.append({"title": title, "action": "create_issue"})
                continue
            body_path = root / str(draft["body_path"])
            labels: Any = draft.get("labels", [])
            requested_labels = (
                [str(label) for label in cast("list[Any]", labels)]
                if isinstance(labels, list)
                else []
            )
            selected_labels = [label for label in requested_labels if label in available_labels]
            skipped_labels = [label for label in requested_labels if label not in available_labels]
            command = [
                "issue",
                "create",
                "--repo",
                repository,
                "--title",
                title,
                "--body-file",
                str(body_path),
            ]
            for label in selected_labels:
                command.extend(("--label", label))
            url = str(_run_gh(command, root=root))
            issue = {"title": title, "url": url, "number": url.rstrip("/").split("/")[-1]}
            remote_issues[title] = issue
            actions.append({"title": title, "action": "created_issue"})
            if skipped_labels:
                actions.append({
                    "title": title,
                    "action": f"skipped_labels:{','.join(skipped_labels)}",
                })

        number = issue.get("number")
        if number is None:
            url = _issue_url(issue)
            number = url.rstrip("/").split("/")[-1] if url else None
        if number is None:
            actions.append({"title": title, "action": "missing_issue_number"})
            continue
        if str(number) in project_items:
            actions.append({"title": title, "action": "present"})
            continue
        if not apply:
            actions.append({"title": title, "action": "add_project_item"})
            continue
        url = _issue_url(issue)
        if url is None:
            actions.append({"title": title, "action": "missing_issue_url"})
            continue
        _run_gh(
            ["project", "item-add", str(project_number), "--owner", owner, "--url", url],
            root=root,
        )
        project_items.add(str(number))
        actions.append({"title": title, "action": "added_project_item"})
    return actions


def main() -> None:
    """Print a safe synchronization plan; writes require explicit ``--apply``."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository",
        default=os.environ.get("GITHUB_REPOSITORY", "edithatogo/reimbursement-atlas"),
    )
    parser.add_argument("--owner", default=None)
    parser.add_argument("--project-number", type=int, default=18)
    parser.add_argument("--title", action="append", default=[])
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    owner = args.owner or args.repository.split("/", maxsplit=1)[0]
    actions = sync_project(
        root=project_root(),
        repository=args.repository,
        owner=owner,
        project_number=args.project_number,
        title_filters=tuple(args.title),
        apply=args.apply,
    )
    counts: dict[str, int] = {}
    for action in actions:
        counts[action["action"]] = counts.get(action["action"], 0) + 1
    print(
        json.dumps({"apply": args.apply, "count": len(actions), "counts": counts}, sort_keys=True)
    )
    for action in actions:
        print(f"{action['action']}: {action['title']}")


if __name__ == "__main__":
    main()

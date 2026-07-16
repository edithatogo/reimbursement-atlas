"""Validate the repository's live or captured branch-protection contract."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, cast
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / ".github" / "branch-protection.example.yml"
ZIZMOR_APP_ID = 15368


def contract_contexts() -> tuple[str, ...]:
    """Read required contexts from the declarative branch-protection example."""
    text = CONTRACT.read_text(encoding="utf-8")
    match = re.search(r"^  contexts:\n(?P<body>(?:    - .+\n)+)", text, flags=re.MULTILINE)
    if match is None:
        message = "branch-protection example has no required contexts"
        raise ValueError(message)
    return tuple(re.findall(r"^    - (.+)$", match.group("body"), flags=re.MULTILINE))


def validate_branch_protection(payload: dict[str, Any]) -> list[str]:
    """Return contract violations without mutating GitHub settings."""
    expected = contract_contexts()
    actual_contexts = tuple(str(item) for item in payload.get("contexts", []))
    errors: list[str] = []
    if payload.get("strict") is not True:
        errors.append("strict required status checks are not enabled")
    if actual_contexts != expected:
        missing = sorted(set(expected) - set(actual_contexts))
        extra = sorted(set(actual_contexts) - set(expected))
        errors.append(f"required context drift: missing={missing}, extra={extra}")
    checks_raw = payload.get("checks", [])
    if not isinstance(checks_raw, list):
        errors.append("required status checks payload is not a list")
        return errors
    checks_raw = cast("list[Any]", checks_raw)
    checks: list[dict[str, Any]] = [
        cast("dict[str, Any]", row) for row in checks_raw if isinstance(row, dict)
    ]
    by_context: dict[str, dict[str, Any]] = {
        str(row["context"]): row for row in checks if row.get("context") is not None
    }
    zizmor = by_context.get("zizmor")
    if zizmor is None:
        errors.append("zizmor is not present in app-bound required checks")
    elif zizmor.get("app_id") != ZIZMOR_APP_ID:
        errors.append(
            "zizmor must be bound to GitHub Actions app "
            f"{ZIZMOR_APP_ID}, got {zizmor.get('app_id')}"
        )
    return errors


def _live_payload(repo: str, token: str) -> dict[str, Any]:
    """Fetch required status checks without printing the bearer token."""
    request = Request(
        f"https://api.github.com/repos/{repo}/branches/main/protection/required_status_checks",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(request, timeout=20) as response:  # noqa: S310 - fixed GitHub HTTPS endpoint
        return json.load(response)


def main(argv: list[str] | None = None) -> int:
    """Validate a JSON fixture or the live GitHub branch-protection response."""
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--json", type=Path, help="captured required_status_checks JSON")
    source.add_argument("--live", action="store_true", help="query GitHub's protected main branch")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"), help="OWNER/REPO")
    args = parser.parse_args(argv)
    if args.live:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token or not args.repo:
            print(
                "--live requires GH_TOKEN/GITHUB_TOKEN and --repo or GITHUB_REPOSITORY",
                file=sys.stderr,
            )
            return 2
        payload = _live_payload(args.repo, token)
        source_name = f"GitHub {args.repo}:main"
    else:
        payload = json.loads(args.json.read_text(encoding="utf-8"))
        source_name = str(args.json)
    errors = validate_branch_protection(payload)
    report = {"source": source_name, "status": "pass" if not errors else "fail", "errors": errors}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

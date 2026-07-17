"""Read back repository security controls without exposing credentials or mutations."""

from __future__ import annotations

import argparse
import json
import os
import subprocess  # nosec B404 - fixed gh API read command
from pathlib import Path
from typing import Any, cast

SECURITY_KEYS = (
    "secret_scanning",
    "secret_scanning_push_protection",
    "secret_scanning_non_provider_patterns",
    "secret_scanning_validity_checks",
)
ENABLED_STATUS = "enabled"  # nosec B105 - GitHub status, not a credential


def _gh_read(repo: str) -> tuple[dict[str, Any] | None, str | None]:
    """Read repository metadata through the authenticated GitHub CLI."""
    try:
        result = subprocess.run(  # nosec B603, B607 - fixed read-only gh command
            ["gh", "api", f"repos/{repo}"],
            capture_output=True,
            check=False,
            text=True,
            timeout=60,
        )
    except FileNotFoundError:
        return None, "gh executable is unavailable"
    except subprocess.TimeoutExpired:
        return None, "GitHub API read timed out"
    except OSError as exc:
        return None, f"GitHub CLI execution failed: {exc}"
    if result.returncode != 0:
        return None, result.stderr.strip() or f"gh api exited {result.returncode}"
    try:
        return cast("dict[str, Any]", json.loads(result.stdout)), None
    except json.JSONDecodeError:
        return None, "GitHub API returned invalid JSON"


def build_report(
    *,
    repo: str,
    payload: dict[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """Build a redacted, machine-readable security control report."""
    if error:
        return {
            "schema_version": "github-security-settings-v1",
            "repository": repo,
            "status": "blocked_environment",
            "mutation_performed": False,
            "network_io": True,
            "error": error,
            "controls": {},
        }
    payload_dict = payload if isinstance(payload, dict) else {}
    security_value = payload_dict.get("security_and_analysis")
    security = cast("dict[str, Any]", security_value) if isinstance(security_value, dict) else {}
    missing_controls: list[str] = []
    controls: dict[str, str] = {}
    for key in SECURITY_KEYS:
        if key not in security:
            missing_controls.append(key)
        control = security.get(key)
        control_dict = cast("dict[str, Any]", control) if isinstance(control, dict) else {}
        controls[key] = str(control_dict.get("status", "unknown"))
    if missing_controls:
        return {
            "schema_version": "github-security-settings-v1",
            "repository": repo,
            "status": "blocked_permissions",
            "mutation_performed": False,
            "network_io": True,
            "error": (
                "GitHub API response omitted security analysis settings; "
                "token scope or API visibility is insufficient"
            ),
            "controls": controls,
            "missing_controls": missing_controls,
            "core_controls_ready": False,
            "advanced_controls_ready": False,
            "next_action": (
                "Run this monitor with a token that can read repository security analysis settings."
            ),
        }
    advanced = all(controls[key] == ENABLED_STATUS for key in SECURITY_KEYS[2:])
    core = all(controls[key] == ENABLED_STATUS for key in SECURITY_KEYS[:2])
    return {
        "schema_version": "github-security-settings-v1",
        "repository": repo,
        "status": "pass" if core and advanced else "blocked_account",
        "mutation_performed": False,
        "network_io": True,
        "controls": controls,
        "core_controls_ready": core,
        "advanced_controls_ready": advanced,
        "next_action": (
            "Enable the two account/plan-bound controls, then rerun this monitor."
            if not advanced
            else "No repository security-setting action is required."
        ),
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    """Write a report containing no response headers, tokens or local paths."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    """Read the repository security settings and write a redacted report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/derived/repo_automation/github_security_settings.json"),
    )
    args = parser.parse_args()
    if not args.repo or "/" not in args.repo:
        report = build_report(repo=args.repo or "unknown", error="repository must be owner/name")
    else:
        payload, error = _gh_read(args.repo)
        report = build_report(repo=args.repo, payload=payload, error=error)
    write_report(args.output, report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

"""Check whether the dashboard checker can adopt the TypeScript 7 channel."""

from __future__ import annotations

import argparse
import json
import subprocess  # nosec B404 - fixed npm metadata commands below
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root, repo_relative

NpmView = Callable[[str, str], tuple[object, str | None]]


def _npm_view(spec: str, field: str, *, cwd: Path) -> tuple[object, str | None]:
    """Read public npm metadata without invoking install or lifecycle scripts."""
    try:
        completed = subprocess.run(  # nosec B603, B607 - fixed npm metadata command
            ["npm", "view", spec, field, "--json"],
            cwd=cwd,
            capture_output=True,
            check=False,
            text=True,
            timeout=60,
        )
    except FileNotFoundError:
        return None, "npm executable is unavailable"
    except subprocess.TimeoutExpired:
        return None, "npm metadata lookup timed out"
    if completed.returncode != 0:
        return None, completed.stderr.strip() or f"npm view exited {completed.returncode}"
    try:
        return json.loads(completed.stdout), None
    except json.JSONDecodeError:
        return completed.stdout.strip(), None


def _peer_supports_typescript7(peer_range: str) -> bool:
    """Conservatively recognise peer ranges that explicitly admit TypeScript 7."""
    normalised = peer_range.replace(" ", "")
    if "*" in normalised or ">=7" in normalised or ">7" in normalised:
        return True
    return any(token in normalised for token in ("^7", "~7", "7.x", "7.*"))


def build_report(  # noqa: PLR0914 - fields mirror the compatibility contract
    root: Path | None = None,
    *,
    npm_view: NpmView | None = None,
) -> dict[str, Any]:
    """Build a non-mutating compatibility report from package and registry metadata."""
    repo = root or project_root()
    dashboard = repo / "apps" / "dashboard"
    package_path = dashboard / "package.json"
    package = cast("dict[str, Any]", json.loads(package_path.read_text(encoding="utf-8")))
    dependencies = cast("dict[str, Any]", package.get("dependencies", {}))
    checker_version = str(dependencies.get("@astrojs/check", "unknown"))
    current_typescript = str(dependencies.get("typescript", "unknown"))

    def default_view(spec: str, field: str) -> tuple[object, str | None]:
        return _npm_view(spec, field, cwd=dashboard)

    view: NpmView = npm_view or default_view

    peer_value, peer_error = view(f"@astrojs/check@{checker_version}", "peerDependencies")
    peer_dependencies = (
        cast("dict[str, object]", peer_value) if isinstance(peer_value, dict) else {}
    )
    peer_range = str(peer_dependencies.get("typescript", ""))
    candidate_value, candidate_error = view("typescript@7", "version")
    candidate_typescript = (
        ", ".join(str(item) for item in cast("list[object]", candidate_value))
        if isinstance(candidate_value, list)
        else str(candidate_value or "")
    )
    errors = [error for error in (peer_error, candidate_error) if error]
    if errors:
        status = "blocked_network" if "timed out" not in " ".join(errors) else "unknown"
    elif _peer_supports_typescript7(peer_range) and candidate_typescript:
        status = "upgrade_available"
    else:
        status = "blocked_peer"
    return {
        "schema_version": "typescript-compatibility-v1",
        "status": status,
        "current_typescript": current_typescript,
        "target_channel": "7.x",
        "candidate_typescript7": candidate_typescript,
        "checker": "@astrojs/check",
        "checker_version": checker_version,
        "checker_peer_typescript": peer_range,
        "upgrade_recommended": status == "upgrade_available",
        "errors": errors,
        "network_io": True,
        "mutation_performed": False,
    }


def _markdown(report: dict[str, Any]) -> str:
    """Render a safe issue/artifact summary without registry payloads."""
    lines = [
        "# TypeScript compatibility canary",
        "",
        f"- Status: `{report['status']}`",
        f"- Current TypeScript: `{report['current_typescript']}`",
        f"- TypeScript 7 candidate: `{report['candidate_typescript7'] or 'unavailable'}`",
        f"- Checker: `{report['checker']}@{report['checker_version']}`",
        f"- Checker peer range: `{report['checker_peer_typescript'] or 'unavailable'}`",
        "- This report performs metadata lookups only; it never changes package files.",
        "",
    ]
    if report["status"] == "upgrade_available":
        lines.extend([
            (
                "TypeScript 7 is admitted by the checker peer contract. Open a normal reviewable "
                "upgrade PR and rerun npm ci, Astro check, build and browser gates."
            ),
            "",
        ])
    elif report.get("errors"):
        lines.extend(["Metadata lookup errors:", ""])
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("TypeScript 7 remains blocked by the current checker peer contract.")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    """Write JSON and Markdown compatibility evidence."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root() / "data" / "derived" / "toolchain",
    )
    args = parser.parse_args()
    report = build_report()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "typescript_compatibility.json"
    markdown_path = args.output_dir / "typescript_compatibility.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_markdown(report), encoding="utf-8")
    print(
        "Wrote TypeScript compatibility evidence: "
        f"{repo_relative(json_path)}, {repo_relative(markdown_path)}"
    )


if __name__ == "__main__":
    main()

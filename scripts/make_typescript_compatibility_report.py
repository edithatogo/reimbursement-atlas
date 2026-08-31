"""Check whether the dashboard checker can adopt the TypeScript 7 channel."""

from __future__ import annotations

import argparse
import json
import re
import subprocess  # nosec B404 - fixed npm metadata commands below
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root, repo_relative

NpmView = Callable[[str, str], tuple[object, str | None]]
MAX_PEER_RANGE_LENGTH = 512
_NUMBER = r"(?:0|[1-9][0-9]*)"
_VERSION_TOKEN = (
    rf"(?:v?{_NUMBER}(?:\.{_NUMBER}){{0,2}}"
    rf"|v?{_NUMBER}\.(?:[xX*](?:\.[xX*])?|{_NUMBER}\.[xX*])"
    r"|[xX*](?:\.[xX*]){0,2})"
)
_COMPARATOR_TOKEN = rf"(?:<=|>=|<|>|=|~|\^)?\s*{_VERSION_TOKEN}"
_COMPARATOR_SET = re.compile(rf"{_COMPARATOR_TOKEN}(?:\s+{_COMPARATOR_TOKEN})*", re.ASCII)
_HYPHEN_PAIR = re.compile(rf"{_VERSION_TOKEN}\s+-\s+{_VERSION_TOKEN}", re.ASCII)


def _npm_view(spec: str, field: str, *, cwd: Path) -> tuple[object, str | None]:
    """Read public npm metadata without invoking install or lifecycle scripts."""
    # npm view treats raw '*' as the default tag, whereas 'x' is a true range.
    if spec == "typescript@*" and field == "version":
        spec = "typescript@x"
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
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError:
        value = completed.stdout.strip()
    if completed.returncode != 0:
        payload = cast("dict[str, object]", value) if isinstance(value, dict) else {}
        raw_error = payload.get("error")
        error = cast("dict[str, object]", raw_error) if isinstance(raw_error, dict) else {}
        version_range = spec.removeprefix("typescript@")
        range_query = (
            spec.startswith("typescript@")
            and field == "version"
            and _peer_range_input_supported(version_range)
        )
        if (
            range_query
            and error.get("code") == "E404"
            and error.get("summary") == f"No match found for version {version_range}"
        ):
            return [], None
        return None, completed.stderr.strip() or f"npm view exited {completed.returncode}"
    return value, None


def _peer_range_input_supported(value: str) -> bool:
    """Accept limited stable-range syntax; npm owns comparator semantics."""
    if not value or len(value) > MAX_PEER_RANGE_LENGTH or not value.isascii():
        return False
    # Reserve one safe-integer increment for npm's shorthand range expansion.
    if any(int(number) >= 2**53 - 1 for number in re.findall(r"[0-9]+", value)):
        return False
    return all(
        _COMPARATOR_SET.fullmatch(clause.strip()) or _HYPHEN_PAIR.fullmatch(clause.strip())
        for clause in value.split("||")
    )


def _stable_versions(value: object) -> list[str] | None:
    """Accept concrete stable versions only; npm, not this helper, parses ranges."""
    values = cast("list[object]", value) if isinstance(value, list) else [value]
    if not all(
        isinstance(item, str)
        and re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", item)
        for item in values
    ):
        return None
    return list(dict.fromkeys(cast("list[str]", values)))


def build_report(  # ruff:ignore[too-many-locals] - fields mirror the compatibility contract
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
    raw_peer_range = peer_dependencies.get("typescript", "")
    peer_range = raw_peer_range.strip() if isinstance(raw_peer_range, str) else ""
    peer_input_supported = _peer_range_input_supported(peer_range)
    candidate_value, candidate_error = view("typescript@7", "version")
    candidates = _stable_versions(candidate_value)
    if candidates is not None and any(not item.startswith("7.") for item in candidates):
        candidates = None
    admitted: list[str] | None = None
    errors = [error for error in (peer_error, candidate_error) if error]
    if not errors and peer_input_supported and candidates:
        admitted_value, admitted_error = view(f"typescript@{peer_range}", "version")
        admitted = _stable_versions(admitted_value)
        if admitted_error:
            errors.append(admitted_error)
    eligible = [item for item in candidates or [] if item in (admitted or [])]
    candidate_typescript = ", ".join(eligible or candidates or [])
    if errors:
        status = "blocked_network" if "timed out" not in " ".join(errors) else "unknown"
    elif not peer_input_supported or not candidates or admitted is None:
        status = "unknown"
        errors.append("npm metadata has unsupported peer input or invalid stable version lists")
    elif eligible:
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

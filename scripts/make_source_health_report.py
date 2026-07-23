"""Generate an actionable report for incomplete source acquisition."""

from __future__ import annotations

import json
import re
from operator import itemgetter
from pathlib import Path
from typing import TypedDict, cast

from reimburse_atlas.io import write_csv
from reimburse_atlas.registry import project_root, read_jsonl, repo_relative


class AcquisitionItem(TypedDict):
    """A redacted source-acquisition handoff item."""

    task_id: str
    status: str
    title: str
    recommended_action: str
    evidence_path: str
    credential_names: list[str]
    review_required_count: int
    operational_blocker_count: int


_MISSING_CREDENTIAL_RE = re.compile(r"Required credential is absent:\s*([A-Z][A-Z0-9_]*)")


def _recommended_action(status: str) -> str:
    if status == "review_required":
        return (
            "Complete the human source/licence review for the gated rows; no additional "
            "automated acquisition is required."
        )
    if status == "blocked_secret":
        return (
            "Provide the required credential through the approved secret store, "
            "then rerun acquisition."
        )
    if status == "blocked_network":
        return (
            "Restore network access or run the documented acquisition command "
            "from an approved network."
        )
    if status == "partial":
        return (
            "Review downloaded-source evidence and resolve remaining licence-gated "
            "or unacquired targets before promotion."
        )
    return (
        "Run the hardened source-download plan and review the acquisition "
        "attempts before promotion."
    )


def _missing_credentials(repo: Path, evidence_path: str) -> list[str]:
    """Extract missing secret names from redacted acquisition evidence."""
    attempts_path = repo / evidence_path
    if not attempts_path.is_file():
        return []
    names: set[str] = set()
    for line in attempts_path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        if record.get("status") != "blocked_secret":
            continue
        match = _MISSING_CREDENTIAL_RE.search(str(record.get("error_summary", "")))
        if match:
            names.add(match.group(1))
    return sorted(names)


def _attempt_status_counts(repo: Path, evidence_path: str) -> dict[str, int]:
    """Summarise redacted acquisition outcomes without exposing payloads."""
    attempts_path = repo / evidence_path
    if not attempts_path.is_file():
        return {}
    counts: dict[str, int] = {}
    for line in attempts_path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        status = str(record.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    return counts


def _classify_partial_task(repo: Path, evidence_path: str) -> tuple[str, int, int]:
    """Separate actionable acquisition failures from licence-only review rows."""
    counts = _attempt_status_counts(repo, evidence_path)
    if not counts:
        return "partial", 0, 1
    review_count = counts.get("skipped_licence_gate", 0)
    operational_count = sum(
        count
        for status, count in counts.items()
        if status
        not in {
            "downloaded",
            "local_cache_available",
            "acquired",
            "acquired_unreviewed",
            "skipped_licence_gate",
        }
    )
    if operational_count == 0 and review_count:
        return "review_required", review_count, 0
    return "partial", review_count, max(operational_count, 1)


def build_source_health_report(root: Path | None = None) -> dict[str, object]:
    """Build a fail-open status report from the generated handoff task list."""
    repo = root or project_root()
    task_path = repo / "data" / "derived" / "final_handoff" / "final_handoff_tasks.jsonl"
    if not task_path.exists():
        return {
            "schema_version": "source-health-acquisition-v1",
            "status": "unknown",
            "incomplete_count": 1,
            "task_ids": ["final_handoff_missing"],
            "items": [
                {
                    "task_id": "final_handoff_missing",
                    "status": "unknown",
                    "title": "Generated final handoff task list is missing",
                    "recommended_action": (
                        "Regenerate final handoff evidence before evaluating "
                        "source acquisition health."
                    ),
                    "evidence_path": "data/derived/final_handoff/final_handoff_tasks.jsonl",
                }
            ],
            "evidence_path": "data/derived/final_handoff/final_handoff_tasks.jsonl",
            "network_io": False,
            "mutation_performed": False,
        }

    incomplete_statuses = {"partial", "blocked_network", "blocked_secret"}
    items: list[AcquisitionItem] = []
    for task in read_jsonl(task_path):
        if task.get("task_group") != "source_ingestion":
            continue
        status = str(task.get("status", ""))
        if status not in incomplete_statuses:
            continue
        task_id = str(task.get("id", "unknown_source_task"))
        evidence_path = str(
            task.get("evidence_path", "data/derived/source_downloads/download_attempts.jsonl")
        )
        credential_names = _missing_credentials(repo, evidence_path)
        review_required_count = 0
        operational_blocker_count = 1
        if status == "partial":
            status, review_required_count, operational_blocker_count = _classify_partial_task(
                repo, evidence_path
            )
        recommended_action = _recommended_action(status)
        if credential_names:
            recommended_action = (
                f"Provide {', '.join(f'`{name}`' for name in credential_names)} through the "
                "approved secret store, then rerun acquisition."
            )
        items.append({
            "task_id": task_id,
            "status": status,
            "title": str(task.get("title", task_id)),
            "recommended_action": recommended_action,
            "evidence_path": evidence_path,
            "credential_names": credential_names,
            "review_required_count": review_required_count,
            "operational_blocker_count": operational_blocker_count,
        })
    items.sort(key=itemgetter("task_id"))
    return {
        "schema_version": "source-health-acquisition-v1",
        "status": "incomplete"
        if any(int(item.get("operational_blocker_count", 0)) > 0 for item in items)
        else ("review_required" if items else "clear"),
        "incomplete_count": len(items),
        "operational_blocker_count": sum(
            int(item.get("operational_blocker_count", 0)) for item in items
        ),
        "review_required_count": sum(int(item.get("review_required_count", 0)) for item in items),
        "task_ids": [item["task_id"] for item in items],
        "items": items,
        "evidence_path": "data/derived/final_handoff/final_handoff_tasks.jsonl",
        "network_io": False,
        "mutation_performed": False,
    }


def _markdown(report: dict[str, object]) -> str:
    """Render the status report for an issue body and human review."""
    status = str(report["status"])
    lines = [
        "# Source acquisition status",
        "",
        f"- Status: `{status}`",
        f"- Incomplete targets: `{report['incomplete_count']}`",
        f"- Operational blockers: `{report.get('operational_blocker_count', 0)}`",
        f"- Licence-review targets: `{report.get('review_required_count', 0)}`",
        "- This report performs no network I/O and no source-cache mutation.",
        "",
    ]
    items = cast("list[dict[str, object]]", report.get("items", []))
    if items:
        lines.extend(["## Actions", ""])
        for item in items:
            lines.extend([
                f"- `{item['task_id']}` ({item['status']}): {item['title']}",
                f"  Action: {item['recommended_action']}",
                f"  Evidence: `{item['evidence_path']}`",
            ])
    else:
        lines.append("No source-ingestion tasks currently require acquisition follow-up.")
    lines.append("")
    return "\n".join(lines)


def write_source_health_report(
    report: dict[str, object], output_dir: Path | None = None
) -> tuple[Path, Path, Path]:
    """Write JSON and Markdown source-health evidence."""
    output = output_dir or project_root() / "data" / "derived" / "source_health"
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "acquisition_status.json"
    markdown_path = output / "acquisition_status.md"
    csv_path = output / "acquisition_status.csv"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_markdown(report), encoding="utf-8")
    items = cast("list[dict[str, object]]", report.get("items", []))
    write_csv(
        [
            {
                "task_id": str(item.get("task_id", "")),
                "status": str(item.get("status", "")),
                "title": str(item.get("title", "")),
                "recommended_action": str(item.get("recommended_action", "")),
                "evidence_path": str(item.get("evidence_path", "")),
                "credential_names": ",".join(
                    str(name) for name in cast("list[object]", item.get("credential_names", []))
                ),
                "review_required_count": int(str(item.get("review_required_count", 0))),
                "operational_blocker_count": int(str(item.get("operational_blocker_count", 0))),
            }
            for item in items
        ],
        csv_path,
    )
    return json_path, markdown_path, csv_path


def main() -> None:
    """Generate source acquisition health evidence."""
    report = build_source_health_report()
    paths = write_source_health_report(report)
    print(f"Wrote source health report: {', '.join(repo_relative(path) for path in paths)}")


if __name__ == "__main__":
    main()

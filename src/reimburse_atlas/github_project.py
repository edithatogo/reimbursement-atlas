"""GitHub Projects import artefacts generated from Conductor context."""

from __future__ import annotations

import json
import re
from pathlib import Path

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.models import ConductorTrackRecord, GitHubProjectItemRecord
from reimburse_atlas.registry import project_root


_PRIORITY_ORDER = ("must", "should", "could", "wont")


def build_github_project_items(
    tracks: list[ConductorTrackRecord],
    *,
    generated_issue_dir: Path | None = None,
) -> list[GitHubProjectItemRecord]:
    """Build deterministic GitHub Project rows from tracks and generated issue drafts."""
    root = project_root()
    issue_dir = generated_issue_dir or root / ".github" / "generated-issues"
    rows: list[GitHubProjectItemRecord] = []
    track_by_title = {track.title: track for track in tracks}
    for track in tracks:
        rows.append(
            GitHubProjectItemRecord(
                id=f"project_track_{track.id}",
                item_type="track",
                title=track.title,
                body_path="conductor/TRACKS.md",
                epic_id=track.id.upper(),
                epic_title=track.title,
                track_id=track.id,
                status="ready",
                priority=track.priority,
                labels=("type:track", f"workstream:{track.workstream}", f"priority:{track.priority}"),
                milestone=_milestone(track.phase),
                project_view=_project_view(track.workstream),
                recommended_action="Create or update a GitHub Project group for this Conductor track.",
            )
        )
    if issue_dir.exists():
        for path in sorted(issue_dir.glob("*.md")):
            parsed = _parse_issue_draft(path)
            epic_title = parsed.get("epic_title", "Generated issue")
            labels = tuple(_split_labels(parsed.get("labels", "")))
            priority = _priority_from_labels(labels)
            track = track_by_title.get(epic_title)
            rows.append(
                GitHubProjectItemRecord(
                    id=f"project_issue_{path.stem.replace('-', '_')}",
                    item_type="issue",
                    title=parsed.get("title", path.stem),
                    body_path=str(path.relative_to(root)),
                    epic_id=parsed.get("epic_id", "GENERATED"),
                    epic_title=epic_title,
                    track_id=track.id if track else None,
                    status=_status_from_labels(labels),
                    priority=priority,
                    labels=labels,
                    milestone=_milestone_from_labels(labels),
                    project_view=_project_view_from_labels(labels),
                    recommended_action=(
                        "Open this generated draft as a GitHub issue and place it on the "
                        "matching Project view once repository credentials are available."
                    ),
                )
            )
    return rows


def write_github_project_items(
    rows: list[GitHubProjectItemRecord],
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write GitHub Project import artefacts and a summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    data = [row.model_dump(mode="json") for row in rows]
    jsonl_path = write_jsonl(data, output_dir / "github_project_items.jsonl")
    csv_path = write_csv(data, output_dir / "github_project_items.csv")
    summary = {
        "project_item_count": len(rows),
        "issue_count": sum(row.item_type == "issue" for row in rows),
        "track_count": sum(row.item_type == "track" for row in rows),
        "must_count": sum(row.priority == "must" for row in rows),
        "blocked_count": sum(row.status == "blocked" for row in rows),
        "views": sorted({row.project_view for row in rows}),
        "milestones": sorted({row.milestone for row in rows}),
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return jsonl_path, csv_path, summary_path


def _parse_issue_draft(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    epic_match = re.search(r"^Epic:\s+`([^`]+)`\s+—\s+(.+)$", text, re.MULTILINE)
    labels_match = re.search(r"^Labels:\s+(.+)$", text, re.MULTILINE)
    return {
        "title": title_match.group(1).strip() if title_match else path.stem,
        "epic_id": epic_match.group(1).strip() if epic_match else "GENERATED",
        "epic_title": epic_match.group(2).strip() if epic_match else "Generated issue",
        "labels": labels_match.group(1).strip() if labels_match else "",
    }


def _split_labels(label_text: str) -> list[str]:
    if not label_text or label_text == "none":
        return []
    return [item.strip() for item in label_text.split(",") if item.strip()]


def _priority_from_labels(labels: tuple[str, ...]) -> str:
    for priority in _PRIORITY_ORDER:
        if f"priority:{priority}" in labels:
            return priority
    if "risk:licence" in labels or "type:security" in labels:
        return "must"
    if "good-first-issue" in labels:
        return "could"
    return "unknown"


def _status_from_labels(labels: tuple[str, ...]) -> str:
    if "blocked" in labels or any(label.startswith("risk:") for label in labels):
        return "blocked"
    if any(label.startswith("phase:release") for label in labels):
        return "ready"
    return "todo"


def _milestone_from_labels(labels: tuple[str, ...]) -> str:
    phase = next((label.split(":", 1)[1] for label in labels if label.startswith("phase:")), None)
    return _milestone(phase or "unscheduled")


def _milestone(phase: str) -> str:
    normalised = phase.replace("_", "-").replace(" ", "-").lower()
    if normalised in {"slice", "1-slice", "phase-1-slice"}:
        return "M1 evidence-grade source slice"
    if normalised in {"hardening", "release-gate", "release"}:
        return "M2 release hardening"
    if normalised in {"analysis", "implementation"}:
        return "M3 policy demonstrators"
    if normalised in {"future", "2-expansion", "phase-2-expansion"}:
        return "M4 expansion roadmap"
    return "M0 project setup"


def _project_view_from_labels(labels: tuple[str, ...]) -> str:
    type_label = next((label for label in labels if label.startswith("type:")), "type:general")
    return _project_view(type_label.split(":", 1)[1])


def _project_view(workstream: str) -> str:
    mapping = {
        "ingestion": "Sources & ingestion",
        "sources": "Sources & ingestion",
        "data-source": "Sources & ingestion",
        "parser": "Sources & ingestion",
        "research": "Research & OSF",
        "osf": "Research & OSF",
        "analysis": "Policy analyses",
        "analytics": "Policy analyses",
        "mapping": "Mappings & ontologies",
        "ontology": "Mappings & ontologies",
        "dashboard": "Dashboard & publication",
        "publication": "Dashboard & publication",
        "automation": "CI/CD & security",
        "security": "CI/CD & security",
        "repo-automation": "CI/CD & security",
        "data-quality": "Quality & release gates",
        "release": "Quality & release gates",
    }
    return mapping.get(workstream, "Project backlog")

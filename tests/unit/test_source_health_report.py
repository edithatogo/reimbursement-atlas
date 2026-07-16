from __future__ import annotations

import json
from pathlib import Path

from scripts.make_source_health_report import build_source_health_report, write_source_health_report


def _write_tasks(root: Path, rows: list[dict[str, object]]) -> None:
    path = root / "data" / "derived" / "final_handoff" / "final_handoff_tasks.jsonl"
    path.parent.mkdir(parents=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_source_health_report_selects_only_incomplete_acquisition_tasks(tmp_path: Path) -> None:
    _write_tasks(
        tmp_path,
        [
            {
                "id": "source_partial",
                "task_group": "source_ingestion",
                "status": "partial",
                "title": "Partial source",
            },
            {
                "id": "source_secret",
                "task_group": "source_ingestion",
                "status": "blocked_secret",
                "title": "Secret source",
            },
            {
                "id": "licence_review",
                "task_group": "source_ingestion",
                "status": "blocked_review",
                "title": "Review source",
            },
            {
                "id": "mapping_partial",
                "task_group": "mapping",
                "status": "partial",
                "title": "Mapping",
            },
        ],
    )
    report = build_source_health_report(tmp_path)
    assert report["status"] == "incomplete"
    assert report["task_ids"] == ["source_partial", "source_secret"]
    assert report["network_io"] is False
    assert report["mutation_performed"] is False
    partial_item = report["items"][0]
    assert "licence-gated" in partial_item["recommended_action"]


def test_source_health_report_surfaces_missing_secret_name_without_secret_value(
    tmp_path: Path,
) -> None:
    _write_tasks(
        tmp_path,
        [
            {
                "id": "source_partial",
                "task_group": "source_ingestion",
                "status": "partial",
                "title": "Partial source",
                "evidence_path": "data/derived/source_downloads/download_attempts.jsonl",
            }
        ],
    )
    attempts = tmp_path / "data" / "derived" / "source_downloads"
    attempts.mkdir(parents=True)
    (attempts / "download_attempts.jsonl").write_text(
        json.dumps({
            "status": "blocked_secret",
            "error_summary": "Required credential is absent: PBS_API_SUBSCRIPTION_KEY.",
            "secret_value": "must-never-be-rendered",
        })
        + "\n",
        encoding="utf-8",
    )

    report = build_source_health_report(tmp_path)
    item = report["items"][0]
    assert item["credential_names"] == ["PBS_API_SUBSCRIPTION_KEY"]
    assert "PBS_API_SUBSCRIPTION_KEY" in item["recommended_action"]
    assert "must-never-be-rendered" not in json.dumps(report)


def test_source_health_report_is_clear_when_acquisition_is_complete(tmp_path: Path) -> None:
    _write_tasks(
        tmp_path,
        [
            {
                "id": "source_ready",
                "task_group": "source_ingestion",
                "status": "ready_local",
                "title": "Ready source",
            }
        ],
    )
    report = build_source_health_report(tmp_path)
    paths = write_source_health_report(report, tmp_path / "report")
    assert report["status"] == "clear"
    assert all(path.exists() for path in paths)
    assert "No source-ingestion tasks" in paths[1].read_text(encoding="utf-8")


def test_source_health_report_fails_open_when_handoff_is_missing(tmp_path: Path) -> None:
    report = build_source_health_report(tmp_path)
    assert report["status"] == "unknown"
    assert report["task_ids"] == ["final_handoff_missing"]

"""Tests for the historical-source archival evidence boundary."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path


def test_historical_download_manifest_is_complete_and_relative(repo_root: Path) -> None:
    """Every discovered target has a checksum-bearing local evidence row."""
    path = repo_root / "data/derived/historical_sources/historical_source_downloads.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 343
    assert {row["status"] for row in rows} <= {"cached", "downloaded", "download_failed"}
    assert all(not str(row["cache_path"]).startswith("/") for row in rows)
    assert all(len(row["checksum_sha256"]) == 64 for row in rows)
    assert all(row["review_status"] == "pending_human_review" for row in rows)


def test_historical_transformation_process_is_bpmn_2(repo_root: Path) -> None:
    """The governed process is a parseable BPMN 2.0 model."""
    path = repo_root / "data/derived/processes/historical_source_transformation.bpmn"
    root = ET.parse(path).getroot()
    assert root.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}definitions"
    process = root.find("{http://www.omg.org/spec/BPMN/20100524/MODEL}process")
    assert process is not None
    task_names = {
        task.attrib["name"]
        for task in process.findall("{http://www.omg.org/spec/BPMN/20100524/MODEL}task")
    }
    assert "Review source terms and permitted reuse" in task_names
    assert "Emit citation, provenance and research package metadata" in task_names

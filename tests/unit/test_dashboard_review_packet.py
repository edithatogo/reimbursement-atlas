from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.make_dashboard_review_packet import build_packet


def test_dashboard_packet_hashes_expected_screenshot_matrix(tmp_path: Path) -> None:
    report = tmp_path / "report/data"
    report.mkdir(parents=True)
    for index in range(36):
        (report / f"{index:02}.png").write_bytes(b"png" + bytes([index]))

    packet = build_packet(tmp_path / "report", "a" * 40)
    schema = json.loads(
        Path("schema/DashboardAutomatedReviewPacket.schema.json").read_text(encoding="utf-8")
    )

    assert packet["status"] == "pass"
    assert packet["screenshot_count"] == 36
    assert packet["human_review_required"] is True
    assert not list(Draft202012Validator(schema).iter_errors(packet))


def test_dashboard_packet_fails_closed_when_artifacts_are_missing(tmp_path: Path) -> None:
    packet = build_packet(tmp_path / "missing", "b" * 40)

    assert packet["status"] == "missing_artifacts"
    assert packet["screenshot_count"] == 0
    assert packet["human_review_required"] is True

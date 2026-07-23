from __future__ import annotations

from pathlib import Path

from scripts.make_dashboard_owner_review_packet import build_packet


def test_owner_packet_is_bounded_and_does_not_imply_approval() -> None:
    packet = build_packet(Path.cwd())

    assert packet["status"] == "pending_accountable_review"
    assert len(packet["routes"]) == 11
    assert packet["screenshot_count"] == 44
    assert packet["automated_test_count"] == 64
    assert len(packet["provenance_inputs"]) >= 4
    assert "approved_within_scope" in packet["accountable_checklist"][-1]

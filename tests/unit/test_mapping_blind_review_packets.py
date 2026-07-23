from __future__ import annotations

from pathlib import Path

from scripts.make_mapping_blind_review_packets import build_packets


def test_current_blind_packets_are_complete_and_hide_hypotheses() -> None:
    cases, manifest = build_packets(Path.cwd())

    assert manifest["status"] == "ready"
    assert len(cases) == 1500
    assert all("proposed_label_hypothesis" not in case for case in cases)
    assert all("split" not in case for case in cases)

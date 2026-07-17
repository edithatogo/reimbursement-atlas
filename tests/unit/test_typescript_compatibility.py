from __future__ import annotations

import json
from pathlib import Path

from scripts.make_typescript_compatibility_report import build_report


def _package(root: Path) -> None:
    path = root / "apps" / "dashboard" / "package.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps({"dependencies": {"@astrojs/check": "0.9.9", "typescript": "6.0.3"}}),
        encoding="utf-8",
    )


def test_typescript7_canary_blocks_on_checker_peer_range(tmp_path: Path) -> None:
    _package(tmp_path)

    def view(_spec: str, field: str) -> tuple[object, str | None]:
        if field == "peerDependencies":
            return {"typescript": "^5.0.0 || ^6.0.0"}, None
        return "7.0.2", None

    report = build_report(tmp_path, npm_view=view)
    assert report["status"] == "blocked_peer"
    assert report["upgrade_recommended"] is False
    assert report["mutation_performed"] is False


def test_typescript7_canary_identifies_reviewable_upgrade(tmp_path: Path) -> None:
    _package(tmp_path)

    def view(_spec: str, field: str) -> tuple[object, str | None]:
        if field == "peerDependencies":
            return {"typescript": "^6.0.0 || ^7.0.0"}, None
        return "7.0.2", None

    report = build_report(tmp_path, npm_view=view)
    assert report["status"] == "upgrade_available"
    assert report["upgrade_recommended"] is True


def test_typescript7_canary_redacts_lookup_errors_to_summaries(tmp_path: Path) -> None:
    _package(tmp_path)

    def view(_spec: str, _field: str) -> tuple[object, str | None]:
        return None, "registry unavailable"

    report = build_report(tmp_path, npm_view=view)
    assert report["status"] == "blocked_network"
    assert report["mutation_performed"] is False
    assert report["errors"] == ["registry unavailable", "registry unavailable"]

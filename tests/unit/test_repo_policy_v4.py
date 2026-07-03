"""Tests for repository raw-data publication policy."""

from __future__ import annotations

from reimburse_atlas.repo_policy import disallowed_tracked_paths, normalise_repo_path


def test_disallowed_tracked_paths_flags_raw_data() -> None:
    """Raw cache files should never be considered publishable tracked files."""
    violations = disallowed_tracked_paths([
        "data/raw_live/au_mbs/live.xml",
        "data/seed/source_registry.jsonl",
        "apps/dashboard/src/pages/index.astro",
    ])
    assert violations == ["data/raw_live/au_mbs/live.xml"]


def test_normalise_repo_path_handles_windows_separators() -> None:
    """Policy checks should be platform independent."""
    assert normalise_repo_path(r".\\data\\raw\\x.csv") == "data/raw/x.csv"

"""Tests for repository raw-data publication policy."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.repo_policy import (
    candidate_public_metadata_path,
    disallowed_public_metadata_values,
    disallowed_tracked_paths,
    normalise_repo_path,
)


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
    assert normalise_repo_path(r".\data\raw\x.csv") == "data/raw/x.csv"


def test_public_metadata_path_scanner_flags_absolute_local_path(tmp_path: Path) -> None:
    """Generated public metadata should not expose absolute local raw paths."""
    metadata = tmp_path / "data" / "derived" / "bundle"
    metadata.mkdir(parents=True)
    leaked = metadata / "source_snapshots.jsonl"
    leaked.write_text('{"local_path": "/mnt/private/raw.csv"}\n', encoding="utf-8")
    safe = metadata / "publication_manifest.json"
    safe.write_text('{"local_path": null}\n', encoding="utf-8")

    violations = disallowed_public_metadata_values(
        tmp_path,
        [
            "data/derived/bundle/source_snapshots.jsonl",
            "data/derived/bundle/publication_manifest.json",
            "docs/example.json",
        ],
    )
    assert violations == ["data/derived/bundle/source_snapshots.jsonl"]


def test_public_metadata_path_scanner_flags_machine_paths_in_any_field(tmp_path: Path) -> None:
    """Generated gate output must not expose its build machine checkout."""
    metadata = tmp_path / "data" / "derived" / "quality"
    metadata.mkdir(parents=True)
    leaked = metadata / "gates.json"
    leaked.write_text('{"cwd": "/Users/example/project"}\n', encoding="utf-8")

    violations = disallowed_public_metadata_values(
        tmp_path,
        ["data/derived/quality/gates.json"],
    )
    assert violations == ["data/derived/quality/gates.json"]


def test_candidate_public_metadata_path_is_narrow() -> None:
    """Docs can mention local cache examples without tripping generated-data scans."""
    assert candidate_public_metadata_path("data/derived/x.jsonl")
    assert candidate_public_metadata_path("apps/dashboard/public/data/x.csv")
    assert not candidate_public_metadata_path("docs/example.json")

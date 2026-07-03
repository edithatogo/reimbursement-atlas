"""Tests for v5 publication manifest generation."""

from __future__ import annotations

from pathlib import Path

from reimburse_atlas.publication import build_publication_manifest, write_publication_manifest


def test_publication_manifest_contains_only_safe_candidate_paths(repo_root: Path) -> None:
    """The default manifest should avoid raw/local cache paths."""
    manifest = build_publication_manifest(root=repo_root)
    assert manifest.artifact_count > 0
    assert all(not artifact.contains_raw_source_payload for artifact in manifest.artifacts)
    assert any(
        artifact.relative_path.endswith("source_registry.jsonl") for artifact in manifest.artifacts
    )


def test_publication_manifest_write(tmp_path: Path, repo_root: Path) -> None:
    """Publication manifest should be writable as JSON."""
    manifest = build_publication_manifest(root=repo_root)
    path = write_publication_manifest(manifest, tmp_path / "publication_manifest.json")
    assert path.exists()
    assert "artifact_count" in path.read_text(encoding="utf-8")

"""Repository policy checks for raw-data and generated-file hygiene."""

from __future__ import annotations

from pathlib import Path

DISALLOWED_RAW_PREFIXES = (
    "data/raw/",
    "data/raw_live/",
    "data/local/",
    "data/cache/",
    "data/processed/",
    "data/public/",
    "lancedb/",
)


def normalise_repo_path(path: str) -> str:
    """Normalise a path as a forward-slash repository-relative path."""
    normalised = path.replace("\\", "/").lstrip("./")
    while "//" in normalised:
        normalised = normalised.replace("//", "/")
    return normalised


def disallowed_tracked_paths(paths: list[str]) -> list[str]:
    """Return tracked files that violate raw-data cache policy."""
    violations: list[str] = []
    for path in paths:
        normalised = normalise_repo_path(path)
        if any(normalised.startswith(prefix) for prefix in DISALLOWED_RAW_PREFIXES):
            violations.append(normalised)
    return sorted(violations)


PUBLIC_METADATA_PREFIXES = (
    "data/seed/",
    "data/derived/",
    "apps/dashboard/public/data/",
)
PUBLIC_METADATA_SUFFIXES = (".json", ".jsonl", ".csv")
ABSOLUTE_LOCAL_PATH_MARKERS = (
    '"local_path": "/',
    '"local_path","/',
    "local_path,/",
    "/Users/",
    "/Volumes/",
    "/home/",
    "file:///",
    ":\\Users\\",
)


def candidate_public_metadata_path(path: str) -> bool:
    """Return whether a tracked path is generated public metadata worth scanning."""
    normalised = normalise_repo_path(path)
    return normalised.endswith(PUBLIC_METADATA_SUFFIXES) and any(
        normalised.startswith(prefix) for prefix in PUBLIC_METADATA_PREFIXES
    )


def disallowed_public_metadata_values(root: Path, paths: list[str]) -> list[str]:
    """Return generated metadata files that leak absolute local raw paths."""
    root_path = root
    violations: list[str] = []
    for path in paths:
        normalised = normalise_repo_path(path)
        if not candidate_public_metadata_path(normalised):
            continue
        file_path = root_path / normalised
        if not file_path.exists():
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        if any(marker in text for marker in ABSOLUTE_LOCAL_PATH_MARKERS):
            violations.append(normalised)
    return sorted(violations)

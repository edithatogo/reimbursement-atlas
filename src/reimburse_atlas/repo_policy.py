"""Repository policy checks for raw-data and generated-file hygiene."""

from __future__ import annotations

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

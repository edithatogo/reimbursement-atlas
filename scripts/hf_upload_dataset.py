"""Upload permissively redistributable seed data to Hugging Face Hub.

This is intentionally a dry-run scaffold. The production version must enforce
licence allowlists before upload and must never upload restricted ontology files.
"""

from __future__ import annotations

from pathlib import Path

PERMISSIVE_ALLOWLIST = {"Apache-2.0", "CC0", "CC-BY", "OGL"}


def discover_seed_files(root: Path = Path("data/seed")) -> list[Path]:
    """Return seed files that are candidates for upload after licence review."""
    return sorted(path for path in root.glob("*") if path.suffix in {".csv", ".jsonl"})


if __name__ == "__main__":
    for candidate in discover_seed_files():
        print(candidate)

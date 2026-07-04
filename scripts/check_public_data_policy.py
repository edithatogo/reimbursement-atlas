"""Fail if ignored raw/local data paths have been committed."""

from __future__ import annotations

import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path

from reimburse_atlas.registry import project_root
from reimburse_atlas.repo_policy import disallowed_public_metadata_values, disallowed_tracked_paths


def tracked_files(root: Path) -> list[str]:
    """Return git-tracked files in a checkout."""
    git = shutil.which("git")
    if git is None:
        msg = "git executable was not found on PATH"
        raise RuntimeError(msg)
    result = subprocess.run(  # nosec B603
        [git, "ls-files"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def main() -> None:
    """Run public-data publication policy checks."""
    root = project_root()
    tracked = tracked_files(root)
    path_violations = disallowed_tracked_paths(tracked)
    metadata_violations = disallowed_public_metadata_values(root, tracked)
    if path_violations or metadata_violations:
        if path_violations:
            print("Disallowed raw/local data paths are tracked:")
            for path in path_violations:
                print(f"- {path}")
        if metadata_violations:
            print("Generated public metadata leaks absolute local paths:")
            for path in metadata_violations:
                print(f"- {path}")
        sys.exit(1)
    print(
        "Public-data policy check passed: no raw/local cache paths are tracked "
        "and no generated metadata leaks absolute local paths."
    )


if __name__ == "__main__":
    main()

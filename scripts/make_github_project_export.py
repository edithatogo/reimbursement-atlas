"""Generate GitHub Project import rows from Conductor tracks and issue drafts."""

from __future__ import annotations

from reimburse_atlas.github_project import build_github_project_items, write_github_project_items
from reimburse_atlas.registry import load_conductor_tracks, project_root, repo_relative


def main() -> None:
    """Generate GitHub Project import artefacts."""
    rows = build_github_project_items(load_conductor_tracks())
    paths = write_github_project_items(
        rows,
        output_dir=project_root() / "data" / "derived" / "github_project",
    )
    print(
        f"Wrote {len(rows)} GitHub Project rows: {', '.join(repo_relative(path) for path in paths)}"
    )


if __name__ == "__main__":
    main()

"""Generate final local-download and environment-dependent handoff checklist."""

from __future__ import annotations

from reimburse_atlas.final_handoff import build_final_handoff_tasks, write_final_handoff_tasks
from reimburse_atlas.registry import project_root, repo_relative


def main() -> None:
    """Generate the final handoff artefacts."""
    rows = build_final_handoff_tasks()
    paths = write_final_handoff_tasks(
        rows,
        output_dir=project_root() / "data" / "derived" / "final_handoff",
    )
    print(
        f"Wrote {len(rows)} final handoff rows: {', '.join(repo_relative(path) for path in paths)}"
    )


if __name__ == "__main__":
    main()

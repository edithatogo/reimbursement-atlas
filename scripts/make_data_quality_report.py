"""Generate data-quality checks across seed and derived artefacts."""

from __future__ import annotations

from reimburse_atlas.data_quality import build_data_quality_checks, write_data_quality_checks
from reimburse_atlas.registry import project_root, repo_relative


def main() -> None:
    """Write generated data-quality report artefacts."""
    rows = build_data_quality_checks()
    paths = write_data_quality_checks(
        rows,
        output_dir=project_root() / "data" / "derived" / "data_quality",
    )
    print(
        f"Wrote {len(rows)} data quality checks: {', '.join(repo_relative(path) for path in paths)}"
    )


if __name__ == "__main__":
    main()

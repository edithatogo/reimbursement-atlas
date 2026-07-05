"""Generate source/schema drift reports."""

from __future__ import annotations

from reimburse_atlas.registry import project_root
from reimburse_atlas.source_drift import (
    build_default_source_drift_report,
    write_source_drift_report,
)


def main() -> None:
    """Write source drift artefacts."""
    rows = build_default_source_drift_report()
    paths = write_source_drift_report(
        rows,
        output_dir=project_root() / "data" / "derived" / "source_drift",
    )
    print(f"Wrote {len(rows)} source drift checks: {', '.join(str(path) for path in paths)}")


if __name__ == "__main__":
    main()

"""Generate architecture-boundary report artefacts."""

from __future__ import annotations

import json

from reimburse_atlas.architecture import build_architecture_report, write_architecture_report
from reimburse_atlas.registry import project_root


def main() -> None:
    """Write architecture-boundary tables."""
    report = build_architecture_report()
    paths = write_architecture_report(
        report,
        output_dir=project_root() / "data" / "derived" / "architecture",
    )
    payload = {"summary": report.summary.as_row(), "paths": [str(path) for path in paths]}
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

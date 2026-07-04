"""Generate release-readiness matrix artefacts."""

from __future__ import annotations

import json

from reimburse_atlas.registry import project_root
from reimburse_atlas.release_readiness import (
    build_release_readiness_report,
    write_release_readiness_report,
)


def main() -> None:
    """Write release-readiness tables."""
    report = build_release_readiness_report()
    paths = write_release_readiness_report(
        report,
        output_dir=project_root() / "data" / "derived" / "release_readiness",
    )
    payload = {"summary": report.summary.as_row(), "paths": [str(path) for path in paths]}
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

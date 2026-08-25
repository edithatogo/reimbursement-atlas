"""Generate canonical external compatibility and governance evidence."""

from __future__ import annotations

import json
from typing import cast

from reimburse_atlas.governance_monitoring import (
    build_governance_monitor_report,
    write_governance_monitor_report,
)
from reimburse_atlas.registry import project_root, repo_relative


def _read_json(relative_path: str) -> dict[str, object]:
    path = project_root() / relative_path
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return cast("dict[str, object]", value) if isinstance(value, dict) else {}


def main() -> None:
    """Write normalized external-control evidence from monitor receipts."""
    report = build_governance_monitor_report(
        typescript_report=_read_json("data/derived/toolchain/typescript_compatibility.json"),
        github_report=_read_json("data/derived/repo_automation/github_security_settings.json"),
    )
    paths = write_governance_monitor_report(
        report,
        output_dir=project_root() / "data/derived/governance_monitoring",
    )
    print(
        json.dumps(
            {
                "summary": report.summary.as_row(),
                "paths": [repo_relative(path) for path in paths],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

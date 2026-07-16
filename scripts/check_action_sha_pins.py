"""Fail when a GitHub Actions workflow introduces an unpinned external action."""

from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.automation import WorkflowUseRecord, scan_workflow_uses
from reimburse_atlas.registry import project_root

ALLOWED_PIN_CLASSES = frozenset({"sha", "local", "docker"})


def find_unpinned_actions(root: Path) -> list[WorkflowUseRecord]:
    """Return external workflow references that are not immutable or local."""
    return [
        record for record in scan_workflow_uses(root) if record.pin_class not in ALLOWED_PIN_CLASSES
    ]


def main() -> int:
    """Print a machine-readable result and fail closed on any violation."""
    violations = find_unpinned_actions(project_root())
    payload = {
        "allowed_pin_classes": sorted(ALLOWED_PIN_CLASSES),
        "status": "pass" if not violations else "fail",
        "violations": [
            {
                "action": record.action,
                "line": record.line,
                "pin_class": record.pin_class,
                "uses": record.uses,
                "workflow": record.workflow,
            }
            for record in violations
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())

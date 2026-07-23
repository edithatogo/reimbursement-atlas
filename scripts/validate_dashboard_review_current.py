"""Fail when scoped dashboard review evidence does not match displayed current state."""

from __future__ import annotations

import json

from reimburse_atlas.dashboard_review import dashboard_review_approved, dashboard_review_evidence
from reimburse_atlas.registry import project_root


def main() -> None:
    """Validate current implementation and displayed-data parity."""
    root = project_root()
    evidence = dashboard_review_evidence(root)
    print(json.dumps(evidence, indent=2, sort_keys=True))
    if not dashboard_review_approved(root):
        message = "dashboard review evidence is stale or incomplete"
        raise SystemExit(message)


if __name__ == "__main__":
    main()

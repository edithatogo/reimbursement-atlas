"""Evidence-derived archive publication gates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

REQUIRED_READY_FLAGS = (
    "repository_release_ready",
    "evidence_release_ready",
    "osf_registration_ready",
)


def archive_publication_gate(root: Path) -> dict[str, Any]:
    """Return the exact gate state used for DOI reservation and publication."""
    summary_path = root / "data/derived/release_readiness/summary.json"
    if not summary_path.is_file():
        return {
            "status": "blocked",
            "reason_code": "release_readiness_missing",
            "missing_or_false": list(REQUIRED_READY_FLAGS),
            "evidence": str(summary_path.relative_to(root)),
        }
    summary = cast(
        "dict[str, Any]",
        json.loads(summary_path.read_text(encoding="utf-8")),
    )
    missing_or_false = [flag for flag in REQUIRED_READY_FLAGS if summary.get(flag) is not True]
    return {
        "status": "ready" if not missing_or_false else "blocked",
        "reason_code": (
            "archive_publication_gates_pass"
            if not missing_or_false
            else "archive_upstream_gates_pending"
        ),
        "missing_or_false": missing_or_false,
        "evidence": str(summary_path.relative_to(root)),
        "summary": {flag: summary.get(flag) for flag in REQUIRED_READY_FLAGS},
    }

"""Build one bounded dashboard packet for accountable scoped review."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.registry import project_root

AUTOMATED = Path("data/derived/dashboard_review/automated_review_packet.json")
OUTPUT = Path("data/derived/dashboard_review/owner_review_packet.json")
PROVENANCE_INPUTS = (
    Path("apps/dashboard/public/status.json"),
    Path("data/derived/source_validation/summary.json"),
    Path("data/derived/evidence_readiness/summary.json"),
    Path("data/derived/release_readiness/summary.json"),
    Path("data/derived/publication_manifest.json"),
)
ROUTES = (
    "/",
    "/analyses/",
    "/analyses/cognitive_vs_procedural_ratio/",
    "/automation/",
    "/crosswalks/",
    "/demonstrators/",
    "/ontologies/",
    "/readiness/",
    "/roadmap/",
    "/sources/",
    "/sources/au_mbs/",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_packet(root: Path) -> dict[str, Any]:
    """Return deterministic evidence and a bounded accountable-review checklist."""
    automated = cast(
        "dict[str, Any]",
        json.loads((root / AUTOMATED).read_text(encoding="utf-8")),
    )
    provenance = [
        {
            "path": path.as_posix(),
            "sha256": _sha256(root / path),
            "byte_size": (root / path).stat().st_size,
        }
        for path in PROVENANCE_INPUTS
        if (root / path).is_file()
    ]
    return {
        "schema_version": "dashboard-owner-review-packet-v1",
        "status": "pending_accountable_review",
        "tested_commit": automated["tested_commit"],
        "automated_status": automated["status"],
        "routes": list(ROUTES),
        "browser_projects": [
            "Chromium desktop",
            "Chromium mobile",
            "Firefox desktop",
            "WebKit desktop",
        ],
        "automated_test_count": automated["test_count"],
        "screenshot_count": automated["screenshot_count"],
        "screenshot_sha256": automated["screenshot_sha256"],
        "provenance_inputs": provenance,
        "accountable_checklist": [
            "Inspect visual hierarchy, clipping and responsive layout on every listed route.",
            "Complete keyboard-only navigation and confirm visible focus and skip navigation.",
            "Complete macOS VoiceOver review in Safari or WebKit and record the exact versions.",
            (
                "Spot-check displayed source, version, checksum, licence and readiness values "
                "against the provenance inputs."
            ),
            "Confirm no raw or restricted source content is exposed.",
            "Record every finding, remediation or bounded waiver.",
            "Use approved_within_scope only; do not claim universal WCAG conformance.",
        ],
        "required_record": "data/derived/dashboard_review/human_review.json",
        "record_schema": "schema/DashboardHumanReviewRecord.schema.json",
    }


def main() -> None:
    """Write the bounded accountable-review packet."""
    root = project_root()
    packet = build_packet(root)
    output = root / OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": packet["status"],
                "tested_commit": packet["tested_commit"],
                "routes": len(cast("list[str]", packet["routes"])),
                "provenance_inputs": len(cast("list[dict[str, Any]]", packet["provenance_inputs"])),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

"""Check that public documentation matches the fail-closed release contract."""

from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.registry import project_root

REQUIRED_README_MARKERS = (
    "## Current public status",
    "CITATION.cff",
    "Apache-2.0",
    "apps/dashboard/public/status.json",
    "evidence-ready",
    "human research review",
)


def validate_public_docs(root: Path) -> list[str]:
    """Return documentation drift or overclaiming errors."""
    readme = (root / "README.md").read_text(encoding="utf-8")
    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    status = json.loads((root / "apps/dashboard/public/status.json").read_text(encoding="utf-8"))
    errors = [
        f"README is missing required marker: {marker}"
        for marker in REQUIRED_README_MARKERS
        if marker not in readme
    ]
    if 'repository-code: "https://github.com/edithatogo/reimbursement-atlas"' not in citation:
        errors.append("CITATION.cff repository-code does not point to the public repository")
    if (
        status.get("evidence", {}).get("status") != "ready"
        and "not evidence-ready" not in readme.lower()
    ):
        errors.append("README must state that the current product is not evidence-ready")
    if status.get("publication", {}).get("status") == "gated" and "manual" not in readme.lower():
        errors.append("README must describe gated publication as manual")
    return errors


def main() -> None:
    """Fail closed when public documentation drifts from generated status."""
    errors = validate_public_docs(project_root())
    if errors:
        raise SystemExit("Public documentation check failed:\n- " + "\n- ".join(errors))
    print("Public documentation check passed: README and citation claims match status gates.")


if __name__ == "__main__":
    main()

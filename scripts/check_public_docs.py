"""Check that public documentation matches the fail-closed release contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

from reimburse_atlas.registry import project_root

REQUIRED_README_MARKERS = (
    "## Current public status",
    "CITATION.cff",
    "Apache-2.0",
    "apps/dashboard/public/status.json",
    "evidence-ready",
    "human research review",
    "docs/RELEASE_VERIFICATION.md",
)
PUBLIC_URL_MARKERS = (
    "https://github.com/edithatogo/reimbursement-atlas",
    "https://edithatogo.github.io/reimbursement-atlas/",
)


def validate_public_docs(root: Path) -> list[str]:
    """Return documentation drift or overclaiming errors."""
    readme = (root / "README.md").read_text(encoding="utf-8")
    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    license_text = (root / "LICENSE").read_text(encoding="utf-8")
    notice_text = (root / "NOTICE").read_text(encoding="utf-8")
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
    if ">=3.14" not in (root / "pyproject.toml").read_text(encoding="utf-8"):
        errors.append("README runtime claim cannot be verified against pyproject.toml")
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        errors.append("LICENSE must contain the canonical Apache License, Version 2.0 text")
    if "Underlying source data" not in notice_text:
        errors.append("NOTICE must distinguish project code from underlying source data terms")
    for url in PUBLIC_URL_MARKERS:
        if url not in readme or urlparse(url).scheme != "https":
            errors.append(f"README is missing canonical HTTPS URL: {url}")
    return errors


def build_public_docs_report(root: Path) -> dict[str, object]:
    """Build a machine-readable report for the documentation freshness gate."""
    errors = validate_public_docs(root)
    return {
        "schema_version": "public-docs-v1",
        "status": "pass" if not errors else "fail",
        "error_count": len(errors),
        "errors": errors,
        "checked_files": [
            "README.md",
            "CITATION.cff",
            "LICENSE",
            "NOTICE",
            "pyproject.toml",
            "apps/dashboard/public/status.json",
        ],
        "canonical_urls": list(PUBLIC_URL_MARKERS),
    }


def main() -> None:
    """Fail closed when public documentation drifts from generated status."""
    root = project_root()
    report_path = root / "data" / "derived" / "repo_automation" / "public_docs_freshness.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = build_public_docs_report(root)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    errors = cast("list[str]", report["errors"])
    if errors:
        raise SystemExit("Public documentation check failed:\n- " + "\n- ".join(errors))
    print("Public documentation check passed: README and citation claims match status gates.")


if __name__ == "__main__":
    main()

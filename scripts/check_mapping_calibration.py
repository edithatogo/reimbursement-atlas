"""Validate mapping workbench calibration artefacts without overclaiming evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reimburse_atlas.registry import project_root

REQUIRED_FILES = (
    "gold_standard_mappings.jsonl",
    "negative_controls.jsonl",
    "mapping_calibration_cases.jsonl",
    "mapping_calibration_summary.jsonl",
)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build_mapping_calibration_report(root: Path) -> dict[str, Any]:
    """Return a structural report with reviewer status kept separate."""
    directory = root / "data" / "derived" / "vertical_slice"
    missing = [name for name in REQUIRED_FILES if not (directory / name).exists()]
    if missing:
        return {
            "schema_version": "mapping-calibration-v1",
            "status": "fail",
            "missing_files": missing,
            "gold_standard_count": 0,
            "negative_control_count": 0,
            "triggered_negative_control_count": 0,
        }

    gold = _read_jsonl(directory / REQUIRED_FILES[0])
    negative = _read_jsonl(directory / REQUIRED_FILES[1])
    cases = _read_jsonl(directory / REQUIRED_FILES[2])
    summary = _read_jsonl(directory / REQUIRED_FILES[3])[0]
    structural_errors = [
        "gold-standard set is empty" if not gold else "",
        "negative-control set is empty" if not negative else "",
        "calibration cases are missing" if not cases else "",
        "calibration rows must identify a reviewer"
        if any(not row.get("reviewer") or not row.get("reviewed_at") for row in [*gold, *negative])
        else "",
    ]
    errors = [error for error in structural_errors if error]
    triggered = int(summary.get("triggered_negative_control_count", 0))
    return {
        "schema_version": "mapping-calibration-v1",
        "status": "fail" if errors else ("review_required" if triggered else "pass"),
        "errors": errors,
        "gold_standard_count": len(gold),
        "negative_control_count": len(negative),
        "calibration_case_count": len(cases),
        "triggered_negative_control_count": triggered,
        "reviewer_signoff_required": True,
        "evidence_ready": False,
    }


def main() -> None:
    """Write the report and fail only on malformed calibration structure."""
    root = project_root()
    report = build_mapping_calibration_report(root)
    path = root / "data" / "derived" / "vertical_slice" / "mapping_calibration_gate.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if report["status"] == "fail":
        raise SystemExit("Mapping calibration validation failed: " + "; ".join(report["errors"]))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

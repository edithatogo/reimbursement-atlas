"""Generate source-readiness grade threshold sensitivity artefacts."""

from __future__ import annotations

import json

from reimburse_atlas.analysis import readiness_grade_sensitivity_rows
from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.registry import load_source_registry, project_root

THRESHOLD_SETS = [
    ("canonical", 11, 8, 5),
    ("strict", 12, 9, 6),
    ("lenient", 10, 7, 4),
]


def main() -> None:
    """Write a sensitivity report without changing canonical readiness grades."""
    root = project_root()
    output = root / "data" / "derived" / "readiness_sensitivity"
    rows = readiness_grade_sensitivity_rows(load_source_registry(), THRESHOLD_SETS)
    write_jsonl(rows, output / "readiness_grade_sensitivity.jsonl")
    write_csv(rows, output / "readiness_grade_sensitivity.csv")
    summary = {
        "threshold_configurations": len(rows),
        "source_count": rows[0]["source_count"] if rows else 0,
        "canonical_configuration": "canonical",
        "interpretation": (
            "Alternative thresholds are diagnostic and do not alter canonical grades."
        ),
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(rows)} readiness sensitivity rows to {output}")


if __name__ == "__main__":
    main()

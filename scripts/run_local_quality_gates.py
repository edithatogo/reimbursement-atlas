"""Run the repo's local quality-gate profile and write machine-readable results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import cast

from reimburse_atlas.local_quality import (
    QualityGateProfile,
    QualityGateRunRecord,
    run_quality_gate,
    specs_for_profile,
    summarise_quality_gate_run,
    write_quality_gate_run,
)
from reimburse_atlas.registry import project_root


def main() -> None:
    """Run selected local quality gates."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        choices=["quick", "ci", "release", "nightly"],
        default="ci",
        help="Quality-gate profile to run.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root() / "data" / "derived" / "local_quality_gates",
        help="Directory for local quality-gate records.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write planned gates without executing them.",
    )
    parser.add_argument(
        "--allow-blocking-failures",
        action="store_true",
        help="Always exit zero after writing results.",
    )
    args = parser.parse_args()

    profile = cast("QualityGateProfile", args.profile)
    records: list[QualityGateRunRecord] = []
    for spec in specs_for_profile(profile):
        print(f"[local-quality] starting {spec.id}", flush=True)
        record = run_quality_gate(spec, dry_run=bool(args.dry_run))
        records.append(record)
        summary = summarise_quality_gate_run(records, profile=profile)
        write_quality_gate_run(records, summary, output_dir=args.output_dir)
        print(f"[local-quality] {record.id}: {record.status}", flush=True)
    summary = summarise_quality_gate_run(records, profile=profile)
    paths = write_quality_gate_run(records, summary, output_dir=args.output_dir)
    payload = {"summary": summary.as_row(), "paths": [str(path) for path in paths]}
    print(json.dumps(payload, indent=2))
    if summary.blocking_failures and not args.allow_blocking_failures:
        sys.exit(1)


if __name__ == "__main__":
    main()

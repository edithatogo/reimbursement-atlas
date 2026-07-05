"""Generate source download plans and optionally attempt safe downloads."""

from __future__ import annotations

import argparse
from pathlib import Path

from reimburse_atlas.registry import load_source_files, project_root
from reimburse_atlas.source_downloads import (
    attempt_download,
    build_download_plan,
    write_download_outputs,
)


def main() -> None:
    """Write source download plan and optional attempt records."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", action="store_true", help="Attempt executable downloads.")
    parser.add_argument(
        "--resume-downloads",
        action="store_true",
        help="Allow curl/wget resume flags for servers that support byte ranges.",
    )
    parser.add_argument("--method", choices=["curl", "wget"], default="curl")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root() / "data" / "derived" / "source_downloads",
    )
    args = parser.parse_args()
    records = load_source_files()
    if args.limit:
        records = records[: args.limit]
    plans = [
        build_download_plan(
            record,
            preferred_method=args.method,
            resume_downloads=args.resume_downloads,
        )
        for record in records
    ]
    attempts = [
        attempt_download(
            record,
            preferred_method=args.method,
            resume_downloads=args.resume_downloads,
        )
        for record in records
        if args.attempt
    ]
    paths = write_download_outputs(plans, attempts, output_dir=args.output_dir)
    print({
        "plans": len(plans),
        "attempts": len(attempts),
        "paths": [str(path) for path in paths],
    })


if __name__ == "__main__":
    main()

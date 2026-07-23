"""Download the complete public openFDA device classification corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reimburse_atlas.openfda_device_acquisition import (
    acquire_complete_device_classifications,
)
from reimburse_atlas.registry import project_root


def main() -> None:
    """Write ignored raw payload and descriptor-free acquisition evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw-output",
        type=Path,
        default=Path("data/raw_live/us_fda_device_classification/complete.json"),
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("data/derived/source_downloads/openfda_device_complete.json"),
    )
    parser.add_argument("--pause-seconds", type=float, default=0.1)
    args = parser.parse_args()
    root = project_root()
    payload, summary = acquire_complete_device_classifications(
        pause_seconds=args.pause_seconds
    )
    raw_output = root / args.raw_output
    summary_output = root / args.summary_output
    raw_output.parent.mkdir(parents=True, exist_ok=True)
    summary_output.parent.mkdir(parents=True, exist_ok=True)
    raw_output.write_text(
        json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary_output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

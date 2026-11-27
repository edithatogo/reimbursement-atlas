"""Validate reference-only Casemix intake and emit a bounded admission receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reimburse_atlas.casemix_handoff import admit_casemix_handoff


def main() -> None:
    """Read a handoff without mutating source registries or human decisions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = admit_casemix_handoff(args.handoff)
    except OSError, ValueError:
        parser.exit(1, "Casemix handoff rejected; no records admitted.\n")
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()

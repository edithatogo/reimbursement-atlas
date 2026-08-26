"""Check live sibling medallion contract parity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reimburse_atlas.medallion_federation import check_live_contract_parity


def main() -> None:
    """Run the network-backed parity check and optionally save its evidence."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = check_live_contract_parity()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if report["status"] != "pass":
        message = "Live medallion federation parity failed"
        raise SystemExit(message)


if __name__ == "__main__":
    main()

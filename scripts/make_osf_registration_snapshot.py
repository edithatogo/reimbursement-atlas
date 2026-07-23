"""Build a canonical immutable OSF registration snapshot from a remote receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from reimburse_atlas.osf_registration import (
    build_remote_registration_snapshot,
    check_registration_drift,
)


def _read_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        message = f"{path} must contain a JSON object"
        raise TypeError(message)
    return cast("dict[str, object]", value)


def main() -> None:
    """Validate the receipt and write the deterministic registration snapshot."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path("data/derived/osf/remote_registration_receipt.json"),
    )
    parser.add_argument(
        "--freeze",
        type=Path,
        default=Path("data/derived/osf/registration_freeze.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/derived/osf/remote_registration_snapshot.json"),
    )
    args = parser.parse_args()

    freeze = _read_object(args.freeze)
    snapshot = build_remote_registration_snapshot(_read_object(args.receipt), freeze)
    result = check_registration_drift(freeze, snapshot)
    if result["status"] != "ready":
        message = f"OSF registration snapshot failed drift validation: {result['reasons']}"
        raise ValueError(message)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "registration_id": snapshot["registration_id"],
                "registration_url": snapshot["registration_url"],
                "snapshot_sha256": snapshot["snapshot_sha256"],
                "output": args.output.as_posix(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

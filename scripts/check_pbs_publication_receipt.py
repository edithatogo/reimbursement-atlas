"""Validate a parent-filled PBS receipt offline; never upload, promote, or archive."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reimburse_atlas.pbs_publication_receipt import evidence_errors, load_receipt


def main() -> int:
    """Report unresolved evidence separately from supplied publication claims."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument(
        "--require-integration",
        action="store_true",
        help="Also require a separately recorded exact-commit software validation envelope.",
    )
    args = parser.parse_args()
    try:
        receipt = load_receipt(args.receipt)
        errors = evidence_errors(receipt, args.evidence_root)
    except OSError, ValueError:
        print(json.dumps({"status": "invalid", "publication_state": "not_asserted"}))
        return 1
    blockers = [*receipt.publication_blockers(), *errors]
    publication = [*blockers]
    if receipt.publication_state != "published_verified":
        publication.append("publication_not_asserted")
    closeout = [*publication]
    if receipt.closeout_delivery is None:
        closeout.append("final_integration_validation_missing")
    required = closeout if args.require_integration else publication
    print(
        json.dumps(
            {
                "status": (
                    "blocked"
                    if required
                    else "receipt_complete"
                    if not closeout
                    else "publication_verified"
                ),
                "validation_scope": (
                    "publication_and_integration" if args.require_integration else "publication"
                ),
                "publication_state": "not_asserted" if blockers else receipt.publication_state,
                "claimed_publication_state": receipt.publication_state,
                "publication_blockers": blockers,
                "closeout_blockers": closeout,
                "viewer_status": receipt.viewer_status,
                "network_performed": False,
                "track_archived": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return int(bool(required))


if __name__ == "__main__":
    raise SystemExit(main())

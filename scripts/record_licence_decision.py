"""Append one validated, checksum-bound licence decision."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.licence_review_validation import validate_licence_review_queue
from reimburse_atlas.registry import project_root


def record_decision(
    decision_path: Path, *, root: Path | None = None, replace: bool = False
) -> None:
    """Validate and append one decision without touching generated queue files."""
    repo = root or project_root()
    queue_path = repo / "data/derived/licence_review/licence_review_queue.jsonl"
    decisions_path = repo / "data/licence_review/decisions.jsonl"
    decision: Any = json.loads(decision_path.read_text(encoding="utf-8"))
    if not isinstance(decision, dict):
        message = "decision file must contain one JSON object"
        raise TypeError(message)
    decision = cast("dict[str, Any]", decision)
    existing = decisions_path.read_text(encoding="utf-8") if decisions_path.exists() else ""
    existing_review_ids = [
        cast("dict[str, Any]", json.loads(line)).get("review_id")
        for line in existing.splitlines()
        if line.strip()
    ]
    if decision.get("review_id") in existing_review_ids and not replace:
        message = f"review_id already exists: {decision.get('review_id')}"
        raise ValueError(message)
    if replace:
        retained = [
            line
            for line in existing.splitlines()
            if not line.strip()
            or json.loads(line).get("review_id") != decision.get("review_id")
        ]
        existing = "\n".join(retained)
    combined = existing.rstrip("\n") + ("\n" if existing.strip() else "")
    combined += json.dumps(decision, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=decisions_path.parent, delete=False
    ) as handle:
        handle.write(combined)
        candidate_path = Path(handle.name)
    try:
        errors = validate_licence_review_queue(
            queue_path,
            root=repo,
            decisions_path=candidate_path,
        )
        if errors:
            message = "decision validation failed:\n- " + "\n- ".join(errors)
            raise ValueError(message)
        decisions_path.parent.mkdir(parents=True, exist_ok=True)
        decisions_path.write_text(combined, encoding="utf-8")
    finally:
        candidate_path.unlink(missing_ok=True)


def main() -> None:
    """Record the JSON decision supplied as the first command-line argument."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decision", type=Path, help="JSON file containing one complete decision")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace an existing decision for the same current review identifier.",
    )
    args = parser.parse_args()
    try:
        record_decision(args.decision, replace=args.replace)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    print("Recorded validated checksum-bound licence decision")


if __name__ == "__main__":
    main()

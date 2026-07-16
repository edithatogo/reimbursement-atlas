"""Apply a complete, reviewable set of resolved GitHub Action pins."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reimburse_atlas.action_pins import ActionPinResolutionRecord, resolve_action_pins
from reimburse_atlas.registry import project_root


class ActionPinUpdateError(RuntimeError):
    """Raised when a pin update cannot be applied atomically."""


def unresolved_external(
    records: list[ActionPinResolutionRecord],
) -> list[ActionPinResolutionRecord]:
    """Return external references that cannot be safely rewritten."""
    return [
        record
        for record in records
        if record.status not in {"resolved", "skipped_sha", "skipped_local_or_docker"}
    ]


def apply_resolutions(
    root: Path,
    records: list[ActionPinResolutionRecord],
) -> int:
    """Rewrite workflow references only when every external ref is resolved."""
    unresolved = unresolved_external(records)
    if unresolved:
        details = "; ".join(
            f"{record.workflow}:{record.line} {record.current_uses}: {record.status}"
            for record in unresolved
        )
        message = f"Refusing partial action-pin update: {details}"
        raise ActionPinUpdateError(message)

    changed = 0
    for record in records:
        if record.status != "resolved" or record.suggested_uses is None:
            continue
        workflow_path = root / record.workflow
        lines = workflow_path.read_text(encoding="utf-8").splitlines(keepends=True)
        index = record.line - 1
        if index < 0 or index >= len(lines):
            message = f"Workflow line moved: {record.workflow}:{record.line}"
            raise ActionPinUpdateError(message)
        line = lines[index]
        occurrences = line.count(record.current_uses)
        if occurrences != 1:
            message = (
                f"Expected one reference to {record.current_uses} at "
                f"{record.workflow}:{record.line}, found {occurrences}"
            )
            raise ActionPinUpdateError(message)
        lines[index] = line.replace(record.current_uses, record.suggested_uses, 1)
        workflow_path.write_text("".join(lines), encoding="utf-8")
        changed += 1
    return changed


def main() -> int:
    """Resolve and apply pins, returning non-zero when safety conditions fail."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=project_root())
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    records = resolve_action_pins(args.root)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps([record.as_row() for record in records], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    try:
        changed = apply_resolutions(args.root, records)
    except ActionPinUpdateError as exc:
        print(str(exc))
        return 1
    print(json.dumps({"resolved_changes": changed, "records": len(records)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

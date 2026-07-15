"""Validate ignored PBS API caches and emit redacted acquisition evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

from reimburse_atlas.pbs_api_evidence import build_pbs_api_evidence, write_pbs_api_evidence
from reimburse_atlas.registry import project_root, repo_relative


def main() -> None:
    """Generate PBS acquisition evidence when the local raw cache is present."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule-path", type=Path)
    parser.add_argument("--item-path", type=Path, action="append", default=[])
    parser.add_argument("--fees-path", type=Path)
    parser.add_argument("--schedule-code", default="4706")
    parser.add_argument("--retrieved-at", default="2026-07-16")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root() / "data" / "derived" / "source_downloads",
    )
    args = parser.parse_args()
    existing = args.output_dir / "pbs_api_acquisition.jsonl"
    if args.schedule_path is None:
        if existing.exists():
            print(f"Preserved existing PBS acquisition evidence: {repo_relative(existing)}")
        else:
            print("PBS raw cache absent; no acquisition evidence generated.")
        return
    if not args.item_path:
        parser.error("--item-path is required when --schedule-path is supplied")
    rows = build_pbs_api_evidence(
        args.schedule_path,
        tuple(args.item_path),
        args.fees_path,
        schedule_code=args.schedule_code,
        retrieved_at=args.retrieved_at,
    )
    paths = write_pbs_api_evidence(rows, output_dir=args.output_dir)
    print(
        f"Wrote {len(rows)} PBS acquisition evidence rows: "
        f"{', '.join(repo_relative(p) for p in paths)}"
    )


if __name__ == "__main__":
    main()

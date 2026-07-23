"""Build licence-scoped CPT mapping evidence in ignored local storage."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from reimburse_atlas.io import write_jsonl
from reimburse_atlas.local_cpt_enrichment import build_local_cpt_candidates
from reimburse_atlas.registry import project_root


def main() -> None:
    """Write a private review packet and descriptor-free public summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cms_archive", type=Path)
    parser.add_argument("mbs_bundle", type=Path)
    parser.add_argument(
        "--local-output",
        type=Path,
        default=Path("data/local/mapping_study/cpt_enrichment/candidates.jsonl"),
    )
    parser.add_argument(
        "--public-summary",
        type=Path,
        default=Path("data/derived/mapping_study/local_cpt_enrichment_summary.json"),
    )
    parser.add_argument("--minimum-score", type=float, default=0.12)
    parser.add_argument("--candidates-per-item", type=int, default=3)
    args = parser.parse_args()
    root = project_root()
    candidates, summary = build_local_cpt_candidates(
        cms_archive=args.cms_archive,
        mbs_bundle=args.mbs_bundle,
        minimum_score=args.minimum_score,
        candidates_per_item=args.candidates_per_item,
    )
    local_output = root / args.local_output
    public_summary = root / args.public_summary
    local_output.parent.mkdir(parents=True, exist_ok=True)
    public_summary.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(candidates, local_output)
    summary["local_packet_sha256"] = hashlib.sha256(local_output.read_bytes()).hexdigest()
    public_summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

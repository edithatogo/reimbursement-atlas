"""Resolve immutable, cycle-scoped mapping-study paths."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CYCLE = "initial"
_CYCLE_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


@dataclass(frozen=True)
class MappingStudyPaths:
    """Paths for one isolated mapping-study cycle."""

    cycle: str
    derived: Path
    review: Path
    frame: Path
    packets: Path
    manifest: Path
    reviewer_a: Path
    reviewer_b: Path
    blind_reviews: Path
    blind_review_summary: Path
    proposals: Path
    adjudications: Path
    owner_packet: Path
    split_plan: Path
    threshold_model: Path
    holdout_predictions: Path
    evaluation: Path


def mapping_study_paths(cycle: str = DEFAULT_CYCLE) -> MappingStudyPaths:
    """Return paths without allowing traversal or ambiguous cycle names."""
    if not _CYCLE_PATTERN.fullmatch(cycle):
        message = "mapping study cycle must match [a-z0-9][a-z0-9_-]{0,63}"
        raise ValueError(message)
    if cycle == DEFAULT_CYCLE:
        derived = Path("data/derived/mapping_study")
        review = Path("data/mapping_study")
        split_plan = Path("data/derived/vertical_slice/mapping_review_pack_plan.json")
    else:
        derived = Path("data/derived/mapping_study") / cycle
        review = Path("data/mapping_study") / cycle
        split_plan = derived / "mapping_review_pack_plan.json"
    packets = derived / "blind_review_packets"
    return MappingStudyPaths(
        cycle=cycle,
        derived=derived,
        review=review,
        frame=derived / "candidate_frame.jsonl",
        packets=packets,
        manifest=packets / "manifest.json",
        reviewer_a=review / "reviewer_a_reviews.jsonl",
        reviewer_b=review / "reviewer_b_reviews.jsonl",
        blind_reviews=review / "blind_reviews.jsonl",
        blind_review_summary=derived / "blind_review_summary.json",
        proposals=review / "adjudication_proposals.jsonl",
        adjudications=review / "adjudications.jsonl",
        owner_packet=derived / "adjudication_owner_packet.json",
        split_plan=split_plan,
        threshold_model=derived / "development_threshold.json",
        holdout_predictions=review / "holdout_predictions.jsonl",
        evaluation=derived / "evaluation_summary.json",
    )


def available_mapping_study_cycles(root: Path) -> list[str]:
    """Return existing frame cycles in deterministic semantic order."""
    cycles = [DEFAULT_CYCLE] if (root / mapping_study_paths().frame).is_file() else []
    derived = root / "data/derived/mapping_study"
    expansions: list[tuple[int, str]] = []
    if derived.is_dir():
        for path in derived.iterdir():
            match = re.fullmatch(r"expansion_v([0-9]+)", path.name)
            if match and int(match.group(1)) >= 2 and (path / "candidate_frame.jsonl").is_file():
                expansions.append((int(match.group(1)), path.name))
    return [*cycles, *(name for _, name in sorted(expansions))]


def latest_mapping_study_cycle(root: Path) -> str:
    """Return the latest existing immutable cycle, or the backward-compatible default."""
    cycles = available_mapping_study_cycles(root)
    return cycles[-1] if cycles else DEFAULT_CYCLE

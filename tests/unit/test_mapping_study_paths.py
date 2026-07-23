from __future__ import annotations

import pytest

from reimburse_atlas.mapping_study_paths import (
    available_mapping_study_cycles,
    latest_mapping_study_cycle,
    mapping_study_paths,
)


def test_initial_paths_remain_backward_compatible() -> None:
    paths = mapping_study_paths()

    assert paths.frame.as_posix() == "data/derived/mapping_study/candidate_frame.jsonl"
    assert paths.split_plan.as_posix() == (
        "data/derived/vertical_slice/mapping_review_pack_plan.json"
    )


def test_named_cycle_paths_are_isolated() -> None:
    paths = mapping_study_paths("expansion_v2")

    assert paths.frame.as_posix().endswith("mapping_study/expansion_v2/candidate_frame.jsonl")
    assert paths.reviewer_a.as_posix().endswith(
        "mapping_study/expansion_v2/reviewer_a_reviews.jsonl"
    )


@pytest.mark.parametrize("cycle", ["../escape", "/absolute", "MixedCase", "space name"])
def test_cycle_rejects_unsafe_names(cycle: str) -> None:
    with pytest.raises(ValueError, match="mapping study cycle"):
        mapping_study_paths(cycle)


def test_cycle_discovery_sorts_versions_numerically(tmp_path) -> None:
    for relative in (
        "data/derived/mapping_study/candidate_frame.jsonl",
        "data/derived/mapping_study/expansion_v10/candidate_frame.jsonl",
        "data/derived/mapping_study/expansion_v2/candidate_frame.jsonl",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")

    assert available_mapping_study_cycles(tmp_path) == [
        "initial",
        "expansion_v2",
        "expansion_v10",
    ]
    assert latest_mapping_study_cycle(tmp_path) == "expansion_v10"

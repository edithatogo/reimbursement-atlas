"""Generate bounded dataset-candidate onboarding assessments."""

from reimburse_atlas.dataset_candidate_assessment import (
    build_dataset_candidate_assessments,
    write_dataset_candidate_assessments,
)
from reimburse_atlas.registry import load_dataset_candidates, load_source_registry, project_root


def main() -> None:
    """Generate candidate assessments from canonical seed records."""
    records = build_dataset_candidate_assessments(load_dataset_candidates(), load_source_registry())
    paths = write_dataset_candidate_assessments(
        records, output_dir=project_root() / "data/derived/dataset_candidates"
    )
    print(f"Wrote {len(records)} candidate assessments: {', '.join(map(str, paths))}")


if __name__ == "__main__":
    main()

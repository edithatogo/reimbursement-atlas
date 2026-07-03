"""Generate local-only ontology concept and mapping-template seed tables."""

from __future__ import annotations

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.registry import project_root
from reimburse_atlas.terminologies import build_mapping_templates, parse_ontology_concepts_csv


def main() -> None:
    """Write ontology concept and mapping-template seed files from synthetic fixtures."""
    root = project_root()
    output_dir = root / "data" / "seed"
    concepts = parse_ontology_concepts_csv(
        root / "tests" / "fixtures" / "ontology_concepts_fixture.csv"
    )
    templates = build_mapping_templates(concepts)
    concept_rows = [concept.model_dump(mode="json") for concept in concepts]
    template_rows = [template.model_dump(mode="json") for template in templates]
    write_jsonl(concept_rows, output_dir / "ontology_concepts.jsonl")
    write_csv(concept_rows, output_dir / "ontology_concepts.csv")
    write_jsonl(template_rows, output_dir / "ontology_mapping_templates.jsonl")
    write_csv(template_rows, output_dir / "ontology_mapping_templates.csv")
    print(f"Wrote ontology seeds: {len(concepts)} concepts and {len(templates)} mapping templates")


if __name__ == "__main__":
    main()

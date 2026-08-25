"""Generate checksum-bound field lineage for governed transformations."""

from __future__ import annotations

import csv

from reimburse_atlas.field_lineage import (
    build_identity_field_lineage,
    sha256_file,
    write_field_lineage_outputs,
)
from reimburse_atlas.registry import project_root, repo_relative


def main() -> None:
    """Generate the first source-registry JSONL-to-CSV lineage projection."""
    root = project_root()
    source = root / "data/seed/source_registry.jsonl"
    output = root / "data/seed/source_registry.csv"
    code = root / "scripts/sync_seed_csvs.py"
    with output.open(encoding="utf-8", newline="") as handle:
        fields = tuple(csv.DictReader(handle).fieldnames or ())
    records = build_identity_field_lineage(
        source_dataset=repo_relative(source),
        output_dataset=repo_relative(output),
        fields=fields,
        transformation_id="sync_seed_csvs:source_registry_jsonl_to_csv:v1",
        code_version=f"sha256:{sha256_file(code)}",
        input_sha256=sha256_file(source),
        output_sha256=sha256_file(output),
        rights_decision_id="source_registry_metadata_scope",
    )
    paths = write_field_lineage_outputs(records, root / "data/derived/field_lineage")
    print({"records": len(records), "paths": [repo_relative(path) for path in paths]})


if __name__ == "__main__":
    main()

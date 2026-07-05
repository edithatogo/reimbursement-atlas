"""Generate source-specific contract validation artefacts."""

from __future__ import annotations

from reimburse_atlas.registry import load_source_files, project_root
from reimburse_atlas.source_contracts import (
    build_source_contract_validations,
    write_source_contract_validations,
)


def main() -> None:
    """Generate source-contract validation artefacts."""
    rows = build_source_contract_validations(load_source_files())
    paths = write_source_contract_validations(
        rows,
        output_dir=project_root() / "data" / "derived" / "source_contracts",
    )
    print(f"Wrote {len(rows)} source-contract rows: {', '.join(str(path) for path in paths)}")


if __name__ == "__main__":
    main()

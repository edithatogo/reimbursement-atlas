"""Generate a data dictionary for public candidate artefacts."""

from __future__ import annotations

from reimburse_atlas.data_dictionary import build_data_dictionary, write_data_dictionary
from reimburse_atlas.registry import project_root


def main() -> None:
    """Write data dictionary artefacts."""
    rows = build_data_dictionary()
    paths = write_data_dictionary(
        rows,
        output_dir=project_root() / "data" / "derived" / "data_dictionary",
    )
    print(f"Wrote {len(rows)} data dictionary rows: {', '.join(str(path) for path in paths)}")


if __name__ == "__main__":
    main()

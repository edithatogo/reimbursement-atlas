"""Generate post-download source-content validation records."""

from __future__ import annotations

from reimburse_atlas.registry import load_source_files, project_root
from reimburse_atlas.source_validation import (
    build_source_content_validations,
    write_source_content_validations,
)


def main() -> None:
    """Write source-content validation artefacts."""
    rows = build_source_content_validations(load_source_files())
    paths = write_source_content_validations(
        rows,
        output_dir=project_root() / "data" / "derived" / "source_validation",
    )
    print(f"Wrote {len(rows)} source validation rows: {', '.join(str(path) for path in paths)}")


if __name__ == "__main__":
    main()

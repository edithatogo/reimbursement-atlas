"""Generate reviewed-source manual acquisition pack artefacts."""

from __future__ import annotations

import json

from reimburse_atlas.acquisition_pack import (
    acquisition_pack_summary,
    build_manual_acquisition_steps,
    write_manual_acquisition_pack,
)
from reimburse_atlas.registry import load_source_files, project_root


def main() -> None:
    """Write manual acquisition-pack files from source-file records."""
    root = project_root()
    steps = build_manual_acquisition_steps(load_source_files())
    paths = write_manual_acquisition_pack(
        steps,
        output_dir=root / "data" / "derived" / "manual_acquisition_pack",
    )
    payload = {"paths": [str(path) for path in paths], **acquisition_pack_summary(steps)}
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

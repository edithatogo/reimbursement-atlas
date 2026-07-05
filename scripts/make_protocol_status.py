"""Generate protocol/report completeness status records."""

from __future__ import annotations

from reimburse_atlas.protocols import build_protocol_status, write_protocol_status
from reimburse_atlas.registry import load_research_questions, project_root


def main() -> None:
    """Write protocol status artefacts."""
    rows = build_protocol_status(load_research_questions())
    paths = write_protocol_status(rows, output_dir=project_root() / "data" / "derived" / "protocols")
    print({"protocols": len(rows), "paths": [str(path) for path in paths]})


if __name__ == "__main__":
    main()

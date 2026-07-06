"""Generate evidence-readiness rows for research questions."""

from __future__ import annotations

from reimburse_atlas.evidence_readiness import build_evidence_readiness, write_evidence_readiness
from reimburse_atlas.registry import project_root, repo_relative


def main() -> None:
    """Write evidence-readiness artefacts."""
    rows = build_evidence_readiness()
    paths = write_evidence_readiness(
        rows,
        output_dir=project_root() / "data" / "derived" / "evidence_readiness",
    )
    print(
        f"Wrote {len(rows)} evidence-readiness rows: "
        f"{', '.join(repo_relative(path) for path in paths)}"
    )


if __name__ == "__main__":
    main()

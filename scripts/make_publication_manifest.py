"""Build a candidate public/Hugging Face dataset publication manifest."""

from __future__ import annotations

from reimburse_atlas.publication import build_publication_manifest, write_publication_manifest
from reimburse_atlas.registry import project_root


def main() -> None:
    """Write the current publication-manifest candidate."""
    manifest = build_publication_manifest()
    path = write_publication_manifest(
        manifest,
        project_root() / "data" / "derived" / "publication_manifest.json",
    )
    print(f"Wrote {manifest.artifact_count} publication artefacts to {path}")


if __name__ == "__main__":
    main()

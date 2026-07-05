"""Generate research-data package metadata."""

from __future__ import annotations

from reimburse_atlas.registry import project_root
from reimburse_atlas.research_package import write_research_package


def main() -> None:
    """Write research package descriptors."""
    paths = write_research_package(project_root() / "data" / "derived" / "research_package")
    print({"paths": [str(path) for path in paths]})


if __name__ == "__main__":
    main()

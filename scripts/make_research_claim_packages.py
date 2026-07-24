"""Generate bounded checksum-ready research claim-package candidates."""

from __future__ import annotations

from reimburse_atlas.registry import project_root
from reimburse_atlas.research_claim_packages import write_claim_package_candidates


def main() -> None:
    """Write all bounded research claim-package candidates."""
    paths = write_claim_package_candidates(project_root())
    print(f"Wrote {len(paths) - 1} research claim packages and summary")


if __name__ == "__main__":
    main()

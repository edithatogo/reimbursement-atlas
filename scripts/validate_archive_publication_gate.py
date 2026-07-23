"""Fail unless every upstream archive-publication gate is currently ready."""

from __future__ import annotations

import json

from reimburse_atlas.archive_publication import archive_publication_gate
from reimburse_atlas.registry import project_root


def main() -> None:
    """Validate the same gate used by Zenodo mutation modes."""
    result = archive_publication_gate(project_root())
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "ready":
        message = "archive publication gates are not ready"
        raise SystemExit(message)


if __name__ == "__main__":
    main()

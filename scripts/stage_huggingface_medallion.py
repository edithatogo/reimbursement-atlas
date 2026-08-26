"""Stage allow-listed medallion configurations for Hugging Face."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reimburse_atlas.medallion_federation import stage_huggingface_medallion
from reimburse_atlas.registry import project_root


def main() -> None:
    """Stage the medallion dataset tree under the requested destination."""
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            stage_huggingface_medallion(project_root(), args.destination),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

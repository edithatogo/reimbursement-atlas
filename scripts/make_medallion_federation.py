"""Generate medallion contract, federation and publication manifests."""

from __future__ import annotations

import json

from reimburse_atlas.medallion_federation import materialise_medallion_federation

if __name__ == "__main__":
    print(json.dumps(materialise_medallion_federation(), indent=2, sort_keys=True))

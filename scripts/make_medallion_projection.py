"""Generate deterministic medallion evidence and promotion projections."""

from __future__ import annotations

import json
from dataclasses import asdict

from reimburse_atlas.medallion_projection import materialise_medallion_projection

if __name__ == "__main__":
    print(json.dumps(asdict(materialise_medallion_projection()), indent=2, sort_keys=True))

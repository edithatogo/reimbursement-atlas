from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.parsers.openfda_device_json import parse_openfda_device_classification


def test_openfda_device_parser_preserves_scope_boundary(tmp_path: Path) -> None:
    path = tmp_path / "devices.json"
    path.write_text(
        json.dumps({
            "results": [
                {
                    "product_code": "ABC",
                    "device_name": "Example device",
                    "definition": "Generic category.",
                    "device_class": "2",
                    "regulation_number": "800.1",
                    "medical_specialty_description": "General",
                }
            ]
        }),
        encoding="utf-8",
    )

    records = parse_openfda_device_classification(path)

    assert records[0].item_code == "ABC"
    assert records[0].payment_amount is None
    assert "not clinical advice" in str(records[0].provenance.transformation_notes)

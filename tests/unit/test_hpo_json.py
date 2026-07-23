from __future__ import annotations

import json
from pathlib import Path

from reimburse_atlas.parsers.hpo_json import parse_hpo_json


def test_hpo_parser_excludes_deprecated_nodes(tmp_path: Path) -> None:
    path = tmp_path / "hp.json"
    path.write_text(
        json.dumps({
            "graphs": [
                {
                    "nodes": [
                        {
                            "id": "http://purl.obolibrary.org/obo/HP_0000002",
                            "lbl": "Abnormality of body height",
                            "meta": {"definition": {"val": "Deviation from expected height."}},
                        },
                        {
                            "id": "http://purl.obolibrary.org/obo/HP_9999999",
                            "lbl": "Old term",
                            "meta": {"deprecated": True},
                        },
                    ]
                }
            ]
        }),
        encoding="utf-8",
    )

    records = parse_hpo_json(path)

    assert [record.item_code for record in records] == ["HP:0000002"]
    assert records[0].provenance.licence_class == "permissive"

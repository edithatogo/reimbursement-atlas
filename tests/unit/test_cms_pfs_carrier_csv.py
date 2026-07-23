from __future__ import annotations

from pathlib import Path

from reimburse_atlas.parsers.cms_pfs_csv import parse_cms_pfs_carrier_csv


def test_carrier_pricing_parser_excludes_descriptors(tmp_path: Path) -> None:
    path = tmp_path / "carrier.txt"
    path.write_text(
        '"2026","01112","05","46505","  ","0000432.49","0000296.85",'
        '" ","0","A","2","0000000.00","0000000.00","9","0000000.00",'
        '"0000000.00"\n',
        encoding="utf-8",
    )

    records = parse_cms_pfs_carrier_csv(
        path,
        source_version="us_cms_pfs_2026_revision_c_carrier",
    )

    assert records[0].item_code == "46505"
    assert records[0].item_label == "PFS code 46505"
    assert records[0].item_description is None
    assert records[0].payment_amount == 432.49
    assert "CPT descriptors are intentionally excluded" in str(
        records[0].provenance.transformation_notes
    )

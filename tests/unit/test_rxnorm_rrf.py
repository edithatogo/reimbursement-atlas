from __future__ import annotations

from pathlib import Path

from reimburse_atlas.parsers.rxnorm_rrf import parse_rxnorm_rrf


def _row(rxcui: str, preferred: str, tty: str, label: str, suppress: str = "N") -> str:
    fields = [
        rxcui,
        "ENG",
        "P",
        "L1",
        "PF",
        "S1",
        preferred,
        "A1",
        "",
        "",
        "",
        "RXNORM",
        tty,
        rxcui,
        label,
        "0",
        suppress,
        "",
    ]
    return "|".join(fields) + "|\n"


def test_rxnorm_parser_selects_active_preferred_concept(tmp_path: Path) -> None:
    path = tmp_path / "RXNCONSO.RRF"
    path.write_text(
        _row("1", "N", "SCD", "Clinical drug")
        + _row("1", "Y", "IN", "Ingredient")
        + _row("2", "Y", "IN", "Suppressed", suppress="Y")
        + _row("3", "Y", "IN", "Non RxNorm").replace("|RXNORM|", "|MTHSPL|"),
        encoding="utf-8",
    )

    records = parse_rxnorm_rrf(path)

    assert [(record.item_code, record.item_label) for record in records] == [("1", "Ingredient")]
    assert records[0].provenance.licence_class == "permissive"

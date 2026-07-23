"""RxNorm Current Prescribable Content RRF parser."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import cast

from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord

RXNORM_URL: HttpUrl = cast(
    "HttpUrl", "https://download.nlm.nih.gov/rxnorm/RxNorm_full_prescribe_07062026.zip"
)
TTY_PRIORITY = {"IN": 0, "PIN": 1, "MIN": 2, "SCD": 3, "SBD": 4, "GPCK": 5, "BPCK": 6}


def parse_rxnorm_rrf(
    path: Path,
    *,
    source_version: str = "rxnorm_cpc_20260706",
    retrieved_at: str | None = None,
) -> list[ScheduleItemRecord]:
    """Parse active English RxNorm concepts and choose one preferred label per RXCUI."""
    selected: dict[str, tuple[tuple[int, int, str], list[str]]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for fields in csv.reader(handle, delimiter="|"):
            if len(fields) < 18:
                continue
            rxcui, language, _ts, _lui, _stt, _sui, preferred = fields[:7]
            source, tty, label, suppress = fields[11], fields[12], fields[14], fields[16]
            if (
                language != "ENG"
                or source != "RXNORM"
                or suppress != "N"
                or tty not in TTY_PRIORITY
            ):
                continue
            rank = (TTY_PRIORITY[tty], 0 if preferred == "Y" else 1, label.casefold())
            current = selected.get(rxcui)
            if current is None or rank < current[0]:
                selected[rxcui] = (rank, [label, tty])
    return [
        ScheduleItemRecord(
            source_id="rxnorm",
            jurisdiction="United States",
            domain="medicines",
            code_system="RXNORM",
            item_code=rxcui,
            item_label=values[0],
            item_description=f"RxNorm term type {values[1]}",
            payment_unit="terminology_concept",
            provenance=ProvenanceRecord(
                source_id="rxnorm",
                source_url=RXNORM_URL,
                retrieved_at=retrieved_at,
                source_version=source_version,
                licence_class="permissive",
                transformation_notes=(
                    "Parsed active English RXNORM-source concepts from NLM Current Prescribable "
                    "Content; one deterministic preferred term retained per RXCUI."
                ),
            ),
        )
        for rxcui, (_rank, values) in sorted(selected.items())
    ]

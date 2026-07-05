"""Parser for MBS historical TXT item-map and descriptor files.

The current MBS downloads page exposes item-map and item-descriptor text files.
The exact raw files should remain in a local ignored cache until redistribution
terms are reviewed. This parser accepts headered pipe/tab/comma text files and a
simple whitespace fallback so maintainers can validate local downloads without
committing them.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from operator import itemgetter
from pathlib import Path
from typing import cast

from pydantic import HttpUrl

from reimburse_atlas.contracts import ProvenanceRecord, ScheduleItemRecord
from reimburse_atlas.parsers.normalise import clean_text, first_present, parse_amount, parse_date

MBS_DOWNLOAD_URL: HttpUrl = cast(
    "HttpUrl",
    "https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/Content/downloads",
)

CODE_FIELDS = (
    "item",
    "itemnum",
    "item_num",
    "item_number",
    "itemnumber",
    "item code",
    "code",
    "mbs_item",
)

LABEL_FIELDS = (
    "descriptor",
    "description",
    "itemdescription",
    "item_descriptor",
    "item descriptors",
    "short_description",
    "label",
)

DOMAIN_FIELDS = ("category", "group", "subgroup", "domain", "service type")
AMOUNT_FIELDS = (
    "schedulefee",
    "schedule_fee",
    "fee",
    "benefit",
    "amount",
    "fee_85",
    "benefit_85",
)
EFFECTIVE_FIELDS = ("startdate", "start_date", "effective_from", "effective date")
RESTRICTION_FIELDS = ("restriction", "note", "annotation", "explanatory_note")


@dataclass(frozen=True)
class MbsTxtParseStats:
    """Small parse diagnostic for MBS TXT pair validation."""

    item_map_rows: int
    descriptor_rows: int
    joined_rows: int
    descriptor_only_rows: int


def parse_mbs_txt_pair(item_map_path: Path, descriptor_path: Path) -> list[ScheduleItemRecord]:
    """Parse an MBS item-map TXT file plus descriptor TXT file into schedule items."""
    item_rows = _read_headered_or_simple_table(item_map_path)
    descriptor_rows = _read_headered_or_simple_table(descriptor_path)
    descriptors = _descriptor_lookup(descriptor_rows)
    records: list[ScheduleItemRecord] = []
    seen_codes: set[str] = set()

    for row in item_rows:
        code = _code(row)
        if code is None:
            continue
        descriptor_row = descriptors.get(code, {})
        label = _label(descriptor_row) or _label(row) or f"MBS item {code}"
        description = _label(descriptor_row) or _label(row)
        effective_from = parse_date(first_present(row, EFFECTIVE_FIELDS))
        records.append(
            ScheduleItemRecord(
                source_id="au_mbs",
                jurisdiction="Australia",
                domain=clean_text(first_present(row, DOMAIN_FIELDS)) or "medical_services",
                code_system="MBS",
                item_code=code,
                item_label=label,
                item_description=description,
                payment_amount=parse_amount(first_present(row, AMOUNT_FIELDS)),
                currency="AUD",
                payment_unit="item",
                effective_from=effective_from,
                restriction_text=clean_text(first_present(row, RESTRICTION_FIELDS)),
                professional_component=True,
                facility_component=False,
                provenance=ProvenanceRecord(
                    source_id="au_mbs",
                    source_url=MBS_DOWNLOAD_URL,
                    effective_date=effective_from,
                    source_version="au_mbs_20260701_txt_pair",
                    licence_class="public_reuse_unclear",
                    transformation_notes=(
                        "Parsed from local MBS item-map and descriptor TXT files; raw files "
                        "remain local until redistribution review."
                    ),
                ),
            )
        )
        seen_codes.add(code)

    for code, descriptor_row in sorted(descriptors.items()):
        if code in seen_codes:
            continue
        label = _label(descriptor_row) or f"MBS item {code}"
        records.append(
            ScheduleItemRecord(
                source_id="au_mbs",
                jurisdiction="Australia",
                domain=(
                    clean_text(first_present(descriptor_row, DOMAIN_FIELDS)) or "medical_services"
                ),
                code_system="MBS",
                item_code=code,
                item_label=label,
                item_description=label,
                currency="AUD",
                payment_unit="item",
                professional_component=True,
                facility_component=False,
                provenance=ProvenanceRecord(
                    source_id="au_mbs",
                    source_url=MBS_DOWNLOAD_URL,
                    source_version="au_mbs_20260701_txt_pair",
                    licence_class="public_reuse_unclear",
                    transformation_notes=(
                        "Descriptor-only row from local MBS descriptor TXT file; payment fields "
                        "require item-map join."
                    ),
                ),
            )
        )
    return records


def parse_stats(item_map_path: Path, descriptor_path: Path) -> MbsTxtParseStats:
    """Return parse counts without serialising derived records."""
    item_rows = _read_headered_or_simple_table(item_map_path)
    descriptor_rows = _read_headered_or_simple_table(descriptor_path)
    parsed_codes = {_code(row) for row in item_rows}
    parsed_codes.discard(None)
    descriptor_codes = {_code(row) for row in descriptor_rows}
    descriptor_codes.discard(None)
    return MbsTxtParseStats(
        item_map_rows=len(item_rows),
        descriptor_rows=len(descriptor_rows),
        joined_rows=len(parsed_codes & descriptor_codes),
        descriptor_only_rows=len(descriptor_codes - parsed_codes),
    )


def _descriptor_lookup(rows: Iterable[Mapping[str, object]]) -> dict[str, Mapping[str, object]]:
    """Build an item-code keyed descriptor lookup."""
    lookup: dict[str, Mapping[str, object]] = {}
    for row in rows:
        code = _code(row)
        if code is not None:
            lookup[code] = row
    return lookup


def _code(row: Mapping[str, object]) -> str | None:
    value = clean_text(first_present(row, CODE_FIELDS))
    if value is None:
        return None
    return value.split()[0].strip()


def _label(row: Mapping[str, object]) -> str | None:
    return clean_text(first_present(row, LABEL_FIELDS))


def _read_headered_or_simple_table(path: Path) -> list[dict[str, object]]:
    """Read a small TXT/CSV table with delimiter detection and simple fallback."""
    text = _read_text_with_fallback(path)
    if not text.strip():
        return []
    sample = text[:4096]
    delimiter = _detect_delimiter(sample)
    if delimiter is not None:
        rows = _read_delimited(text, delimiter)
        if _has_code_like_header(rows):
            return rows
    return _read_simple_lines(text)


def _detect_delimiter(sample: str) -> str | None:
    """Detect common MBS TXT delimiters."""
    counts = {delimiter: sample.count(delimiter) for delimiter in ("|", "\t", ",", ";")}
    delimiter, count = max(counts.items(), key=itemgetter(1))
    return delimiter if count > 0 else None


def _read_delimited(text: str, delimiter: str) -> list[dict[str, object]]:
    reader = csv.DictReader(text.splitlines(), delimiter=delimiter)
    if reader.fieldnames is None:
        return []
    return [dict(row) for row in reader]


def _has_code_like_header(rows: list[dict[str, object]]) -> bool:
    if not rows:
        return False
    headers = {key.lower().strip() for key in rows[0]}
    return any(field in headers for field in CODE_FIELDS)


def _read_simple_lines(text: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in text.splitlines():
        cleaned = clean_text(line)
        if cleaned is None:
            continue
        parts = cleaned.split(maxsplit=1)
        if not parts:
            continue
        rows.append({"item_number": parts[0], "description": parts[1] if len(parts) > 1 else ""})
    return rows


def _read_text_with_fallback(path: Path) -> str:
    """Read text using UTF-8 first, then permissive legacy encodings."""
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def fixed_width_tokenize(line: str, widths: tuple[int, ...]) -> tuple[str, ...]:
    """Split a line by fixed column widths.

    This is the Python reference implementation for `mojo/fixed_width_tokenizer.mojo`.
    Returns one string per width, with trailing whitespace stripped.
    """
    tokens: list[str] = []
    pos = 0
    for width in widths:
        token = line[pos : pos + width].rstrip()
        tokens.append(token)
        pos += width
    return tuple(tokens)


def tokenize_mbs_txt_line(
    line: str,
    *,
    delimiter: str | None = None,
) -> tuple[str, ...]:
    """Tokenize one MBS TXT line using delimiter detection or fixed-width fallback."""
    if delimiter is not None and delimiter in line:
        return tuple(part.strip() for part in line.split(delimiter))
    return fixed_width_tokenize(line, widths=(5, 2, 70, 10, 12, 8, 6))

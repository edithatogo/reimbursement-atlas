"""Small parser normalisation helpers shared by source prototypes."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Protocol


class XmlLikeElement(Protocol):
    """Tiny XML element protocol needed by parser normalisation."""

    tag: str
    text: str | None

    def iter(self) -> Iterable[XmlLikeElement]:
        """Yield this element and descendants."""
        ...


def clean_text(value: object | None) -> str | None:
    """Return stripped text or ``None`` for empty values."""
    if value is None:
        return None
    text = str(value).replace("\xa0", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text or None


def parse_amount(value: object | None) -> float | None:
    """Parse public price-like strings such as '$42.10' or '1,234.56'."""
    text = clean_text(value)
    if text is None:
        return None
    text = text.replace("$", "").replace(",", "")
    try:
        return float(Decimal(text))
    except InvalidOperation:
        return None
    except ValueError:
        return None


def parse_date(value: object | None) -> date | None:
    """Parse ISO-like dates used in fixtures and many public extracts."""
    text = clean_text(value)
    if text is None:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()  # noqa: DTZ007
        except ValueError:
            continue
    return None


def first_present(row: Mapping[str, object], names: tuple[str, ...]) -> object | None:
    """Return the first non-empty value from a row using case-insensitive keys."""
    lowered = {key.lower().strip(): value for key, value in row.items()}
    for name in names:
        value = lowered.get(name.lower())
        if clean_text(value) is not None:
            return value
    return None


def child_text(element: XmlLikeElement, names: tuple[str, ...]) -> str | None:
    """Return the first child text for a set of possible XML tag names."""
    wanted = {name.lower() for name in names}
    for child in element.iter():
        tag = child.tag.split("}")[-1].lower()
        if tag in wanted:
            return clean_text(child.text)
    return None

"""Pinned Global Medicines Atlas v4 identity consumer."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

_COMMIT = re.compile(r"[0-9a-f]{40}")
_DIGEST = re.compile(r"[0-9a-f]{64}")
_PRODUCER = "edithatogo/global-medicines-atlas"


class GmaContractError(ValueError):
    """Raised when a consumer contract cannot prove its pinned GMA identity."""


@dataclass(frozen=True)
class GmaContractBinding:
    """One immutable Global Medicines Atlas identity for a consumer."""
    producer_repository: str
    dataset: str
    revision: str
    path: str
    object_sha256: str
    source_id: str
    layer: str


def bind_gma_contract(contract: bytes) -> GmaContractBinding:
    """Bind a parsed GMA contract without acquiring or republishing data."""
    try:
        document: dict[str, Any] = json.loads(contract)
        producer = document["authority"]["producer_repository"]
        location = document["location"]
        source = document["source"]
    except (KeyError, TypeError, json.JSONDecodeError):
        raise GmaContractError("invalid GMA contract") from None
    if producer != _PRODUCER:
        raise GmaContractError("GMA producer identity is required")
    revision = location.get("revision")
    digest = location.get("sha256")
    if not isinstance(revision, str) or _COMMIT.fullmatch(revision) is None:
        raise GmaContractError("GMA revision must be immutable")
    if not isinstance(digest, str) or _DIGEST.fullmatch(digest) is None:
        raise GmaContractError("GMA object digest is invalid")
    fields = ("dataset", "path")
    if any(
        not isinstance(location.get(field), str) or not location[field]
        for field in fields
    ):
        raise GmaContractError("GMA location is invalid")
    if any(
        not isinstance(source.get(field), str) or not source[field]
        for field in ("source_id", "layer")
    ):
        raise GmaContractError("GMA source identity is invalid")
    return GmaContractBinding(
        producer,
        location["dataset"],
        revision,
        location["path"],
        digest,
        source["source_id"],
        source["layer"],
    )

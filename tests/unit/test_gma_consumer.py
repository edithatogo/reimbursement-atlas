"""Pinned GMA contract consumer boundary."""

from __future__ import annotations

import json

import pytest

from reimburse_atlas.gma_consumer import bind_gma_contract


def contract() -> bytes:
    return json.dumps({
        "authority": {"producer_repository": "edithatogo/global-medicines-atlas"},
        "location": {
            "dataset": "edithatogo/australian-benefits-medallion",
            "revision": "a" * 40,
            "path": "gold/mbs/services.parquet",
            "sha256": "b" * 64,
        },
        "source": {"source_id": "au-mbs", "layer": "gold"},
    }).encode()


def test_binds_only_a_pinned_gma_identity() -> None:
    binding = bind_gma_contract(contract())
    assert binding.producer_repository == "edithatogo/global-medicines-atlas"
    assert binding.revision == "a" * 40


def test_rejects_mutable_or_non_gma_identity() -> None:
    mutable = json.loads(contract())
    mutable["location"]["revision"] = "main"
    with pytest.raises(ValueError, match="revision"):
        bind_gma_contract(json.dumps(mutable).encode())
    foreign = json.loads(contract())
    foreign["authority"]["producer_repository"] = "example/producer"
    with pytest.raises(ValueError, match="producer"):
        bind_gma_contract(json.dumps(foreign).encode())


@pytest.mark.parametrize("field", ["location", "source"])
def test_rejects_non_object_contract_sections(field: str) -> None:
    malformed = json.loads(contract())
    malformed[field] = []

    with pytest.raises(ValueError, match="invalid GMA contract"):
        bind_gma_contract(json.dumps(malformed).encode())

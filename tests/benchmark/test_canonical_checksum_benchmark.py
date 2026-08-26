from reimburse_atlas.backfill_replay import canonical_sha256


def test_canonical_checksum_throughput(benchmark) -> None:
    payload = {
        "source_id": "benchmark-public-metadata",
        "snapshot": "2026-08-26",
        "rows": [{"code": str(index), "value": index} for index in range(100)],
    }

    digest = benchmark(canonical_sha256, payload)

    assert len(digest) == 64

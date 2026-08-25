"""Narrow safeguards for deterministic checksum-ledger scanning."""

from pathlib import Path


def test_gitleaks_allowlist_is_limited_to_schema_validated_checksum_evidence() -> None:
    config = Path(".gitleaks.toml").read_text(encoding="utf-8")
    workflow = Path(".github/workflows/security-assurance.yml").read_text(encoding="utf-8")
    assert "useDefault = true" in config
    assert "data/derived/historical_sources/backfill_replay/" in config
    assert "contracts/medallion/v3/fixtures/" in config
    assert "data/raw_live" not in config
    assert "--config .gitleaks.toml" in workflow

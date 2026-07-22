from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_registry_readiness_contract_is_fail_closed() -> None:
    text = (ROOT / "docs" / "REGISTRY_READINESS.md").read_text(encoding="utf-8")
    assert "repository_ready_external_gates_pending" in text
    assert "Apache-2.0" in text
    assert "provider licences" in text
    assert "#532" in text
    assert "#533" in text
    assert "#534" in text
    assert "does not establish a DOI" in text

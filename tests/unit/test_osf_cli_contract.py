"""Tests for the unauthenticated OSF CLI contract checker."""

import pytest

from scripts.check_osf_cli_contract import validate_contract


def _fake_pinned_run(_binary: str, *args: str) -> str:
    """Return the stable help markers without invoking an external binary."""
    if args == ("--version",):
        return "1.0.0\n"
    return (
        "Export a node snapshot deterministic research profile upload versions "
        "Create and inspect OSF registrations --node --conflict"
    )


def test_osf_cli_contract_accepts_pinned_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    """The required unauthenticated command surface is enforced in CI."""
    monkeypatch.setattr("scripts.check_osf_cli_contract._run", _fake_pinned_run)
    assert validate_contract("osf") == []


def test_osf_cli_contract_rejects_wrong_version(monkeypatch: pytest.MonkeyPatch) -> None:
    """Version drift must fail before any credentialed command is attempted."""
    def _fake_old_run(_binary: str, *args: str) -> str:
        return "0.3.2\n" if args == ("--version",) else ""

    monkeypatch.setattr("scripts.check_osf_cli_contract._run", _fake_old_run)
    assert "expected OSF CLI 1.0.0" in validate_contract("osf")[0]

"""Tests for branch-protection contract validation."""

from __future__ import annotations

from scripts.check_branch_protection import (
    ZIZMOR_APP_ID,
    contract_contexts,
    validate_branch_protection,
)


def _payload() -> dict[str, object]:
    contexts = list(contract_contexts())
    return {
        "strict": True,
        "contexts": contexts,
        "checks": [{"context": context, "app_id": ZIZMOR_APP_ID} for context in contexts],
    }


def test_branch_protection_contract_passes_for_expected_payload() -> None:
    assert validate_branch_protection(_payload()) == []


def test_branch_protection_contract_rejects_zizmor_binding_drift() -> None:
    payload = _payload()
    checks = payload["checks"]
    assert isinstance(checks, list)
    next(row for row in checks if row["context"] == "zizmor")["app_id"] = 57789
    errors = validate_branch_protection(payload)
    assert "zizmor must be bound" in errors[0]


def test_branch_protection_contract_rejects_context_drift() -> None:
    payload = _payload()
    payload["contexts"] = list(payload["contexts"])[1:]
    assert "required context drift" in validate_branch_protection(payload)[0]

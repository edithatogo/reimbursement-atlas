"""Tests for the GitHub security settings readback contract."""

from __future__ import annotations

from scripts.check_github_security_settings import build_report


def test_build_report_distinguishes_account_blocker() -> None:
    """Core controls can pass while unavailable advanced settings stay blocked."""
    report = build_report(
        repo="edithatogo/reimbursement-atlas",
        payload={
            "security_and_analysis": {
                "secret_scanning": {"status": "enabled"},
                "secret_scanning_push_protection": {"status": "enabled"},
                "secret_scanning_non_provider_patterns": {"status": "disabled"},
                "secret_scanning_validity_checks": {"status": "disabled"},
            }
        },
    )
    assert report["status"] == "blocked_account"
    assert report["core_controls_ready"] is True
    assert report["advanced_controls_ready"] is False
    assert report["mutation_performed"] is False


def test_build_report_passes_only_when_all_controls_are_enabled() -> None:
    """The monitor must not infer advanced coverage from core scanning."""
    enabled = {"status": "enabled"}
    report = build_report(
        repo="edithatogo/reimbursement-atlas",
        payload={
            "security_and_analysis": dict.fromkeys(
                (
                    "secret_scanning",
                    "secret_scanning_push_protection",
                    "secret_scanning_non_provider_patterns",
                    "secret_scanning_validity_checks",
                ),
                enabled,
            )
        },
    )
    assert report["status"] == "pass"
    assert report["advanced_controls_ready"] is True


def test_build_report_records_environment_block_without_secrets() -> None:
    """Missing CLI/authentication is explicit and redacted."""
    report = build_report(repo="edithatogo/reimbursement-atlas", error="gh unavailable")
    assert report["status"] == "blocked_environment"
    assert report["controls"] == {}
    assert "token" not in str(report).lower()

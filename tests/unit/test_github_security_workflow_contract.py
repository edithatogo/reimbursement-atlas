"""Contract checks for scheduled GitHub security-settings monitoring."""

from pathlib import Path


def test_security_settings_workflow_is_readback_only() -> None:
    """The workflow must have the minimum issue/artifact permissions and no PATCH."""
    workflow = Path(".github/workflows/github-security-settings.yml").read_text(encoding="utf-8")
    assert "schedule:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "contents: read" in workflow
    assert "issues: write" in workflow
    assert "check_github_security_settings.py" in workflow
    assert "gh issue edit 191" in workflow
    assert "gh api --method PATCH" not in workflow
    assert "actions/upload-artifact@" in workflow

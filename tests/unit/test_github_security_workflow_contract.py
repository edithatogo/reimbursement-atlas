"""Contract checks for scheduled GitHub security-settings monitoring."""

from pathlib import Path


def test_security_settings_workflow_is_readback_only() -> None:
    """The workflow must have the minimum issue/artifact permissions and no PATCH."""
    workflow = Path(".github/workflows/github-security-settings.yml").read_text(encoding="utf-8")
    assert "schedule:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "contents: read" in workflow
    assert "issues: write" in workflow
    assert "GH_TOKEN: ${{ secrets.GH_SECURITY_SETTINGS_TOKEN || github.token }}" in workflow
    assert "administration:read" in workflow
    assert "check_github_security_settings.py" in workflow
    assert "gh issue edit 191" in workflow
    assert "gh api --method PATCH" not in workflow
    assert "actions/upload-artifact@" in workflow


def test_huggingface_destination_monitor_only_writes_github_issue_evidence() -> None:
    """Destination monitoring may synchronize its issue without mutating Hugging Face."""
    workflow = (
        Path(__file__).parents[2] / ".github/workflows/huggingface-destination.yml"
    ).read_text(encoding="utf-8")
    assert "contents: read" in workflow
    assert "issues: write" in workflow
    assert "GH_TOKEN: ${{ github.token }}" in workflow
    assert "gh issue edit 320" in workflow
    assert "actions/upload-artifact@" in workflow
    assert "HF_TOKEN" not in workflow
    assert "git push" not in workflow
    assert "huggingface.co" not in workflow

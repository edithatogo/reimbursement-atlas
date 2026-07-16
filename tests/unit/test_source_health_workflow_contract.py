"""Contract tests for the scheduled source-health monitor."""

from __future__ import annotations

from pathlib import Path


def test_source_health_issue_permissions_are_job_scoped(repo_root: Path) -> None:
    """Only the source-health job may mutate issue state."""
    workflow = (repo_root / ".github" / "workflows" / "source-health.yml").read_text(
        encoding="utf-8"
    )
    global_permissions, jobs = workflow.split("jobs:", maxsplit=1)
    source_health_job = jobs.split("\n  source-health:", maxsplit=1)[1]

    assert "permissions:\n  contents: read" in global_permissions
    assert "issues: write" not in global_permissions
    assert "permissions:" in source_health_job
    assert "contents: read" in source_health_job
    assert "issues: write" in source_health_job
    assert "if: failure()" in source_health_job
    assert "if: always()" in source_health_job

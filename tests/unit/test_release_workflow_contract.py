"""Contract tests for least-privilege release provenance permissions."""

from __future__ import annotations

from pathlib import Path


def test_release_workflow_scopes_write_and_attestation_permissions_to_build(
    repo_root: Path,
) -> None:
    """Preflight must not inherit release mutation or OIDC permissions."""
    workflow = (repo_root / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    global_permissions, jobs = workflow.split("jobs:", maxsplit=1)
    build_job = jobs.split("\n  build:", maxsplit=1)[1]

    assert "permissions:\n  contents: read" in global_permissions
    assert "contents: write" not in global_permissions
    assert "id-token: write" not in global_permissions
    assert "attestations: write" not in global_permissions
    assert "permissions:" in build_job
    assert "contents: write" in build_job
    assert "id-token: write" in build_job
    assert "attestations: write" in build_job

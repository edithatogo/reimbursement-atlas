"""Contract tests for least-privilege release provenance permissions."""

from __future__ import annotations

from pathlib import Path


def test_release_workflow_scopes_write_and_attestation_permissions_to_build(
    repo_root: Path,
) -> None:
    """Preflight must not inherit release mutation or OIDC permissions."""
    workflow = (repo_root / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "permissions:\n  contents: read" in workflow
    assert "build:\n    needs: preflight\n    runs-on: ubuntu-latest\n    permissions:" in workflow
    assert "      contents: write\n      id-token: write\n      attestations: write" in workflow

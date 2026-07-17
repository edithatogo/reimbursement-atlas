from __future__ import annotations

from pathlib import Path


def test_typescript_compatibility_workflow_is_read_only_until_upgrade_is_available(
    repo_root: Path,
) -> None:
    workflow = (repo_root / ".github" / "workflows" / "typescript-compatibility.yml").read_text(
        encoding="utf-8"
    )
    assert "workflow_dispatch" in workflow
    assert "contents: read" in workflow
    assert "issues: write" in workflow
    assert "typescript-compatibility" in workflow
    assert "upgrade_available" in workflow
    assert "npm ci" not in workflow

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
    assert "pixi run archive-publication-gate" in workflow


def test_release_workflow_attests_and_verifies_all_release_subject_classes(
    repo_root: Path,
) -> None:
    """Every uploaded release subject must have workflow-bound provenance first."""
    workflow = (repo_root / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    for subject_path in (
        "dist/*",
        "reimbursement-atlas-*.tar.gz",
        "data/derived/sbom/*.json",
        "release-manifest.json",
    ):
        assert f"subject-path: {subject_path}" in workflow
        assert (
            "for artifact in dist/* reimbursement-atlas-*.tar.gz data/derived/sbom/*.json "
            "release-manifest.json"
        ) in workflow
        assert 'gh attestation verify "$artifact"' in workflow

    assert "Verify release attestations before upload" in workflow
    assert "softprops/action-gh-release" in workflow
    assert "--format json" in workflow
    assert "data/derived/attestations/*.json" in workflow


def test_zenodo_workflow_consumes_exact_attested_github_release(repo_root: Path) -> None:
    workflow = (repo_root / ".github/workflows/zenodo-preflight.yml").read_text(encoding="utf-8")

    assert "release_tag:" in workflow
    assert 'gh release download "$RELEASE_TAG"' in workflow
    assert 'test "$(jq -r \'.commit\' release-manifest.json)" = "$(git rev-parse HEAD)"' in workflow
    assert ".verificationResult.statement.subject[]" in workflow
    assert '--source-ref "refs/tags/$RELEASE_TAG"' in workflow
    assert 'pixi run release-identity "${args[@]}"' in workflow

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_coverage_uses_bounded_xdist_workers() -> None:
    pyproject = ROOT.joinpath("pyproject.toml").read_text(encoding="utf-8")

    assert 'pytest-xdist = ">=3.8.0"' in pyproject
    assert 'coverage = "python -m pytest -n 4 --dist worksteal ' in pyproject


def test_selective_profiles_are_explicitly_local_and_bounded() -> None:
    pyproject = ROOT.joinpath("pyproject.toml").read_text(encoding="utf-8")

    assert '"slow: tests excluded only from opt-in fast local feedback;' in pyproject
    assert "test-fast = \"python -m pytest -q -m 'not slow'\"" in pyproject
    assert 'test-changed = "python -m pytest -q -n 0 --testmon ' in pyproject
    assert 'test-benchmark = "python -m pytest -q -n 0 --benchmark-only ' in pyproject
    assert 'coverage-sysmon = "COVERAGE_CORE=sysmon python -m pytest -n 4 ' in pyproject


def test_authoritative_ci_does_not_use_selective_profiles() -> None:
    workflows = ROOT.joinpath(".github/workflows")

    for workflow in workflows.glob("*.yml"):
        content = workflow.read_text(encoding="utf-8")
        assert "pixi run test-fast" not in content, workflow.name
        assert "pixi run test-changed" not in content, workflow.name
        assert "--testmon" not in content, workflow.name


def test_heavy_pull_request_workflows_cancel_superseded_runs() -> None:
    workflows = (
        "ci.yml",
        "data-smoke.yml",
        "release-readiness.yml",
        "repo-automation.yml",
        "security.yml",
        "uv-quality.yml",
    )

    for workflow in workflows:
        content = ROOT.joinpath(".github/workflows", workflow).read_text(encoding="utf-8")
        assert "concurrency:" in content, workflow
        assert "cancel-in-progress: true" in content, workflow


def test_pages_uses_bounded_browser_smoke() -> None:
    pages = ROOT.joinpath(".github/workflows/pages.yml").read_text(encoding="utf-8")

    assert "npm run test:browser -- --project=desktop-chromium" in pages

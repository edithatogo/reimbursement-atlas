from __future__ import annotations

from pathlib import Path

from reimburse_atlas.automation import (
    automation_control_records,
    classify_action_pin,
    scan_workflow_uses,
    workflow_policy_records,
    workflow_policy_summary,
)


def test_classify_action_pin_variants() -> None:
    assert classify_action_pin("actions/checkout@" + "a" * 40) == "sha"
    assert classify_action_pin("actions/checkout@v6") == "major"
    assert classify_action_pin("owner/action@v1.2.3") == "minor"
    assert classify_action_pin("owner/action@main") == "floating"
    assert classify_action_pin("./.github/actions/local") == "local"
    assert classify_action_pin("docker://alpine:latest") == "docker"


def test_workflow_policy_records_detect_checkout_and_permissions(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "ci.yml").write_text(
        """
name: CI
on: [push]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          persist-credentials: false
      - uses: prefix-dev/setup-pixi@v0.10.0
""".strip()
        + "\n",
        encoding="utf-8",
    )
    uses = scan_workflow_uses(tmp_path)
    assert [record.pin_class for record in uses] == ["major", "minor"]
    policies = workflow_policy_records(tmp_path)
    summary = workflow_policy_summary(policies)
    assert summary["fail"] == 0
    assert any(
        record.gate == "checkout_persist_credentials_false" and record.status == "pass"
        for record in policies
    )
    assert any(
        record.gate == "action_reference_pinning" and record.status == "warn" for record in policies
    )


def test_workflow_policy_records_flag_missing_permissions(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "release.yml").write_text(
        """
name: Release
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@main
""".strip()
        + "\n",
        encoding="utf-8",
    )
    policies = workflow_policy_records(tmp_path)
    assert any(
        record.gate == "explicit_permissions" and record.status == "warn" for record in policies
    )
    assert any(
        record.gate == "action_reference_pinning" and record.status == "fail" for record in policies
    )


def test_automation_controls_are_stable_for_repo_root() -> None:
    root = Path(__file__).resolve().parents[2]
    controls = automation_control_records(root)
    ids = {record.id for record in controls}
    expected = {
        "ci_python_quality",
        "renovate",
        "dependabot",
        "data_publication_gates",
        "local_quality_orchestrator",
    }
    assert expected <= ids

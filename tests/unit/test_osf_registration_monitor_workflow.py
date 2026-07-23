"""Policy checks for the read-only OSF registration monitor."""

from pathlib import Path

ROOT = Path(__file__).parents[2]
WORKFLOW = ROOT / ".github/workflows/osf-registration-monitor.yml"


def test_monitor_is_scheduled_and_does_not_mutate_osf() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert 'cron: "23 4 * * *"' in workflow
    assert "https://api.osf.io/v2/registrations/$registration_id/" in workflow
    assert "-X POST" not in workflow
    assert "-X PATCH" not in workflow
    assert "files upload" not in workflow
    assert "registration_choice" not in workflow


def test_monitor_validates_snapshot_and_updates_only_bounded_issue() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "pixi run osf-registration-snapshot" in workflow
    assert "issues: write" in workflow
    assert "gh issue comment 532" in workflow
    assert "<!-- osf-registration-monitor -->" in workflow
    assert "Papers and preprints remain excluded." in workflow

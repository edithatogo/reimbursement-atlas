# Session v139: GitHub issue-body sync automation

Date: 2026-07-17

## Scope

Make generated GitHub issue-body reconciliation reproducible and safe by default.

## Evidence

- `scripts/sync_github_project.py` now requests remote issue bodies and reports
  `update_issue_body` when generated content differs.
- GitHub's normalized final newline is ignored during comparison.
- Body writes require explicit `--apply`; issue closure, promotion and destructive
  operations remain unavailable.
- `pixi run github-project-sync --title 'Keep generated issue acceptance criteria and status synchronized'`
  detected the drift on issue #370, and after explicit reconciliation reported only
  `present`.
- Focused project-handoff/unit tests passed.

## Outcome

The manual output-issue reconciliation is now represented by a repeatable dry-run/apply
contract and linked to the existing generated-issue synchronization track.

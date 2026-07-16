# v126 Actions SHA-enforcement audit

## Scope

Close the remaining repository-level gap in immutable GitHub Actions enforcement without changing
the solo-maintainer review model or broadening workflow permissions.

## Actions

- Read the live repository Actions permissions and workflow token settings.
- Verified all tracked workflow `uses:` references are full 40-character commit SHAs.
- Enabled `sha_pinning_required=true` through the GitHub repository API while preserving
  `default_workflow_permissions=read`, `can_approve_pull_request_reviews=false` and the existing
  allowed-action policy.
- Commented on and closed issue #352 with the REST read-back evidence.

## Result

Mutable action tags are now blocked by the repository control plane as well as local/CI workflow
policy checks. No secrets, source payloads, workflow permissions or review requirements changed.

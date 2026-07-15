# Conductor session: GitHub advanced secret-scanning state

## Scope

Verify the live GitHub security settings and address the remaining repository-owned hardening
recommendation without claiming account-level controls that are not active.

## Evidence

- `gh api repos/edithatogo/reimbursement-atlas` confirms provider secret scanning, push protection and
  Dependabot security updates are enabled.
- The same endpoint reports `secret_scanning_non_provider_patterns.status=disabled` and
  `secret_scanning_validity_checks.status=disabled`.
- An idempotent repository API enablement attempt did not change either value.
- Main branch protection enforces all 21 quality, security and harness contexts, administrator
  enforcement, linear history, conversation resolution, force-push protection and deletion protection.

## Changes

- Added issue #191 and placed it on Project #18.
- Updated the security and Project documentation to distinguish verified controls from the account-level
  limitation.
- Kept the single-maintainer no-approval policy explicit while retaining mandatory status checks.
- Regenerated issue drafts, Project exports, dashboard mirrors and release evidence.

## Decision

Treat #191 as account-configuration work. Do not enable a false-positive release gate, and do not report
non-provider scanning or validity checks as active until the GitHub settings API shows `enabled`.

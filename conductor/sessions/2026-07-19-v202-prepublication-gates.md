# v202 Pre-publication implementation slice

Date: 2026-07-19

## Implemented

- Removed the circular OSF readiness condition: complete drafted protocols are now
  ready for registration review; registration remains a separate state.
- Added a regression test for drafted protocol readiness.
- Updated OSF provisioning to accept and report an existing public project instead
  of rejecting it. Newly created projects remain private until explicitly changed.
- Regenerated protocol status, OSF plan, release readiness and final handoff outputs.
- Built the static dashboard successfully: 94 pages, zero Astro/TypeScript errors,
  zero warnings, and zero npm audit vulnerabilities.

## Current blockers preserved

- OSF project `q8cnx` is public, but the registration freeze is unapproved and all
  15 sync rows remain `publish_allowed: false`; no OSF upload or registration was
  submitted.
- Hugging Face candidate validation passes, but remote mutation remains fail-closed
  on research/evidence/policy readiness and publication-manifest licence gates.
- Licence decisions remain 171 approved and 6 blocked. The six changed checksums
  require fresh row-level review and were not silently re-approved.
- Papers and final research publication were not attempted.

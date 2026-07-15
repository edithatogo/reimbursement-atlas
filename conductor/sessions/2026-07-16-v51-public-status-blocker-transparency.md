# v51 public status blocker transparency

## Scope

Expose current non-software release blockers as machine-readable public status records and render
them on the dashboard without implying approval.

## Implemented

- Added stable blocker IDs, categories, statuses, evidence paths and next actions to
  `apps/dashboard/public/status.json` generation.
- Added a homepage section listing the current gates requiring action.
- Added unit coverage for fail-closed blocker generation.
- Added the requirement to the public-product track specification, plan and backlog.
- Regenerated GitHub issue and Project artefacts.
- Created live issue [#221](https://github.com/edithatogo/reimbursement-atlas/issues/221) and
  added it to Project 18.

## Current blocker records

- `licence_review`: 155 checksum-bound candidates remain pending human review.
- `evidence_release`: evidence release is not approved.
- `research_publication`: research publication remains gated.
- `osf_registration`: OSF registration is not approved.

## Verification

- Public status unit tests pass.
- Astro typecheck and build pass.
- GitHub Pages asset-path check passes with `PUBLIC_DEPLOY_TARGET=github-pages`.
- Dashboard quality check passes.

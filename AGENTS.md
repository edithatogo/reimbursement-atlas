# Repository Agent Contract

This is a solo-maintainer repository. Automated checks, not a second human
reviewer, are the protected-branch merge gate.

## Before changing code

1. Read `conductor/INDEX.md`, `conductor/TRACKS.md`, and the relevant track.
2. Preserve source-specific licence restrictions and keep raw payloads in
   ignored local storage.
3. Treat generated evidence as a projection of repository state, never as an
   authorization receipt.

## Required workflow

1. Work on a branch and use a pull request; do not push directly to `main`.
2. Add or update tests for behavioral changes.
3. Run `pixi run local-quality-quick` while iterating and
   `pixi run local-quality` before requesting merge.
4. Regenerate affected Conductor, issue, Project, package, dashboard, readiness,
   and handoff outputs.
5. Require the configured hosted checks and merge through branch protection.
6. Verify the merged tree, synchronize local `main`, and remove the feature
   branch only after merge.

## Boundaries

- Never commit credentials, raw restricted data, local absolute paths, or
  restricted descriptors.
- Do not claim missing source coverage as negative evidence.
- Keep repository, evidence, publication, and external-registry readiness as
  distinct states.
- Do not submit papers or preprints unless the owner gives separate explicit
  authorization.
- Never manufacture human, independent-review, licence, or publication
  approvals. Record unavailable external controls as blocked with evidence.

# Current-main header reconciliation

## Objective

Separate the current merged repository commit from the latest external monitor evidence after
PR #450 was squash-merged.

## Evidence

- Current `main`: `be33424c4b4f7d257ccb69529fe3d50d79fc149b`.
- Latest monitor evidence was collected on the merge parent:
  - OSF: `29591535952`
  - Zenodo: `29591537888`
  - source health: `29591540127`
  - Hugging Face destination: `29591542182`
  - GitHub security settings: `29591544121`
- Documentation freshness, release readiness, public-data policy and citation checks passed.

## Outcome

The authoritative headers now report the actual `main` commit and explicitly identify the monitor
parent commit. No external project, publication destination or account security setting was
mutated.

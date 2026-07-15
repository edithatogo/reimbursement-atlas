# Session v63: scheduled source acquisition

Date: 2026-07-16

## Scope

Make the existing source-health monitor perform a fresh hardened acquisition attempt on its
weekly schedule and on manual dispatch, while preserving the repository's raw-source and
credential boundaries.

## Changes

- Added `pixi run source-download-attempt` before source validation.
- Injected `PBS_API_SUBSCRIPTION_KEY` only from the GitHub Actions secret store.
- Kept raw downloads on the ephemeral runner and excluded `data/raw_live/` from uploaded paths.
- Retained derived acquisition attempts, source validation, contracts, drift and readiness
  evidence as the reviewable output. The first live run exposed a missing artifact path for
  acquisition attempts; that path is now included explicitly.
- Kept the issue lifecycle fail-open: partial, network-blocked and credential-blocked
  acquisition remains visible rather than failing as a false source-health success.

## Acceptance

The workflow must pass actionlint, workflow-policy, zizmor and repository CI. A missing PBS
secret must produce a redacted `blocked_secret` attempt, not a leaked credential or raw upload.

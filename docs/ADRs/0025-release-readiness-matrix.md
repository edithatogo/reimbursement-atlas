# ADR 0025: Release-readiness matrix

## Status
Accepted

## Context

The project has many local and external gates: Ruff, basedpyright, pytest coverage, Bandit, npm audit, pip-audit, SBOMs, public-data policy, dashboard build, GitHub workflow posture, architecture boundaries and source-publication manifests. A single CI pass/fail signal hides important differences between local failures, network blockers and advisory hardening gaps.

## Decision

Add a release-readiness matrix that consumes generated gate artefacts and reports required blockers separately from warnings. Public release is considered ready only when every required gate passes.

## Consequences

- The repo can honestly report that all local gates pass while external/network gates remain blocked.
- Release readiness becomes dashboard-visible and machine-readable.
- Optional hardening work, such as GitHub Action SHA pinning, remains visible even when not a required data-release blocker.

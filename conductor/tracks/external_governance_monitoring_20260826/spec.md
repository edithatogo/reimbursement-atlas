# External governance monitoring

## Overview

Unify the existing TypeScript 7/Astro compatibility canary and GitHub security-settings readback into deterministic governance evidence without conflating unavailable external controls with repository release blockers.

## Requirements

- Continue the scheduled, read-only TypeScript 7 compatibility canary.
- Classify checker incompatibility and registry/network unavailability as external dependency states.
- Record unavailable GitHub account/plan-bound non-provider secret scanning and validity checks as externally blocked.
- Preserve provider secret scanning and push-protection observations separately from account-level controls.
- Project each external control into release readiness as `required: false`.
- Regenerate Project, dashboard, readiness, package and handoff evidence from the canonical monitor report.

## Acceptance criteria

- A deterministic governance-monitor report contains stable reason codes, evidence paths, ownership scope, required-for-repository-release flags and recommended actions.
- Scheduled TypeScript and GitHub security workflows generate and upload the canonical report without mutating dependencies or security settings.
- Blocked external controls remain visible in release readiness but do not increment `required_blocker_count` or make `repository_release_ready` false.
- Tests cover peer incompatibility, account capability limits, permission/network failures, upgrade availability and release-readiness isolation.
- Generated issue and GitHub Project rows reference the track.

## Non-functional constraints

- Do not weaken repository security, typing, CI or branch protection.
- Do not store tokens, API response headers, raw account data or local absolute paths.
- Monitoring remains read-only; issue synchronization may report state but cannot enable account settings or upgrade dependencies.

## External gates

- Astro checker support for TypeScript 7 remains controlled by upstream package peer metadata.
- GitHub advanced secret-scanning availability remains controlled by account plan/capability and API visibility.

## Out of scope

- Forcing TypeScript 7 through unsupported peer ranges.
- Treating account-level feature availability as repository implementation failure.
- Mutating GitHub account settings.

## Authoritative inputs

- `.github/workflows/typescript-compatibility.yml`
- `.github/workflows/github-security-settings.yml`
- `data/derived/toolchain/typescript_compatibility.json`
- `data/derived/repo_automation/github_security_settings.json`
- `src/reimburse_atlas/release_readiness.py`

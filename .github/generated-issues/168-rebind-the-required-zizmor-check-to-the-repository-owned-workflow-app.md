# Rebind the required zizmor check to the repository-owned workflow app

Epic: `REL-001` — Release readiness and architecture gates

Labels: type:security, type:supply-chain, type:repo-automation, phase:hardening

Status: `done`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: only the required `zizmor` app binding was changed.
- [x] Strict protection and all 20 required status contexts were preserved.
- [x] GraphQL and REST read-back confirm `zizmor` is bound to GitHub Actions app `15368`, not Advanced Security app `57789`.
- [x] Conductor, documentation and GitHub issue evidence are updated.

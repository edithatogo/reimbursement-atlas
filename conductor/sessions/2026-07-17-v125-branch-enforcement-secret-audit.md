# v125 branch-enforcement and secret-control audit

## Scope

Recheck the live GitHub repository security settings after the source-acquisition merge and apply
only non-destructive branch hardening that does not create a second-reviewer dependency.

## Actions

- Read back repository security settings and `main` branch protection with the authenticated GitHub
  CLI.
- Confirmed secret scanning, push protection and Dependabot security updates are enabled.
- Attempted to enable GitHub non-provider secret-pattern scanning and secret-validity checks through
  the repository API. GitHub retained both settings as disabled.
- Enabled administrator enforcement on `main` through the branch-protection API.
- Added the limitation and read-back evidence to issue #191; no secret value was read or changed.

## Result

Administrator bypass of required CI/security/harness checks is no longer possible. Required review
count remains zero, preserving the solo-maintainer merge path. Account/feature-level secret controls
remain blocked and must not be represented as enabled by repository code or generated readiness.

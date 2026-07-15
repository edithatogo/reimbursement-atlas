# Conductor session: secret-scanning control scope

## Evidence

- The authenticated owner is a user account; the repository has no active ruleset.
- GitHub's live repository settings report provider secret scanning, push protection and Dependabot
  updates enabled.
- The same settings report non-provider pattern scanning and validity checks disabled.
- The repository API enablement attempt did not change either setting.

## Interpretation

Non-provider pattern scanning and partner-pattern validity checks are separate controls. Validity
checks do not provide generic non-provider pattern coverage.

## Decision

Keep issue #191 open as account/security-configuration work and do not claim either control as active
until the applicable GitHub settings show `enabled`.

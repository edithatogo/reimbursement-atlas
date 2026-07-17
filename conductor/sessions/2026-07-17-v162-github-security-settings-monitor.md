# Session: v162 GitHub security-settings monitor

Date: 2026-07-17

## Scope

Make the remaining account-bound GitHub security controls observable without weakening the
repository's fail-closed security posture or handling credentials in generated artefacts.

## Implemented

- Added `scripts/check_github_security_settings.py` for a read-only `gh api` readback.
- Added unit coverage for enabled, blocked-account and blocked-environment states.
- Added a workflow contract test and scheduled `.github/workflows/github-security-settings.yml`.
- The workflow uploads redacted JSON evidence and synchronizes issue #191 without PATCH calls.
- Linked the monitor to the Conductor backlog, generated issue acceptance and security documentation.

## Live evidence

The authenticated repository reports provider scanning and push protection enabled, with
`secret_scanning_non_provider_patterns=disabled` and `secret_scanning_validity_checks=disabled`.
The report therefore remains `blocked_account`; no secret values or tokens were recorded.

## External boundary

The repository API enablement request did not change the advanced settings. Chrome navigation to
the GitHub security page was blocked by enterprise browser policy. Account/plan enablement remains
an external maintainer action; compensating repository controls remain active and tested.

## Follow-up correction

The first merged Actions dispatch authenticated with `GITHUB_TOKEN` but the repository metadata
response omitted `security_and_analysis`. The monitor now reports `blocked_permissions` with a
redacted missing-controls list and an explicit API-visibility next action. It reserves
`blocked_account` for complete readbacks that show the advanced settings disabled.

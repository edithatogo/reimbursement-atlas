# Session: security and live-evidence audit

Date: 2026-07-17

## Scope

Re-audit the remaining blocked source-validation and repository-security rows after
the protected merge of the generated-project status fix.

## Evidence checked

- The repository working tree is clean on `main` at `b862f1a`.
- The ignored local PBS API response parses with `parse_pbs_api_csv` into 10,000
  `ScheduleItemRecord` values. The first observed item is `10001J` and the extract
  effective date is `2026-07-01`.
- The PBS response remains `acquired_unreviewed`; no human-reviewed monthly extract
  or licence decision has been added, so the corresponding Conductor row remains
  blocked.
- The real MBS evidence remains the July 2026 TXT pair. It is not an XML release,
  so the XML validation row remains blocked; the TXT bundle still requires human
  licence/research review before publication.
- CMS CLFS and PFS remain AMA/licence-gated metadata-only records. CMS ASP remains a
  metadata-only landing-page record. No restricted payload was downloaded or tracked.
- GitHub repository settings were queried through the authenticated repository API.
  `secret_scanning`, `secret_scanning_push_protection` and Dependabot security updates
  are enabled. GitHub returned `disabled` for both
  `secret_scanning_non_provider_patterns` and `secret_scanning_validity_checks` after
  a fail-closed enablement request. The public personal-repository/account capability
  boundary remains external; the repository-owned Gitleaks history workflow is the
  compensating control.

## Decision

No blocked row is promoted. The machine-level parser and policy checks pass, but
evidence readiness must continue to distinguish acquisition from reviewed-source,
licence and human research approval.

## Gates

- PBS local parser smoke: pass.
- Public-data policy: pass.
- Seed synchronisation: pass.
- Repository security settings query: pass with non-provider and validity checks
  externally blocked.


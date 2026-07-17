# Conductor session: v168 current preflight evidence

Date: 2026-07-17

## Scope

Run the current read-only OSF and Zenodo preflights on merged `main` after the documentation
refresh, then verify the sanitized OSF project artifact.

## Evidence

- Current merged commit: `fc47649`.
- OSF workflow run `29569972259` passed discovery and the component plan with pinned
  `osf-cli-go v1.0.0`.
- Sanitized OSF discovery contained 28 accessible projects and the private `Reimbursement Atlas`
  project `q8cnx`.
- OSF provisioning, registration, upload and publication were skipped; no OSF mutation occurred.
- Zenodo workflow run `29569972301` passed metadata and repository-readiness checks and recorded
  `mutation_performed: false` and `doi_created: false`.

## Boundary

These are current operational preflight records only. Protocol, licence, methods, evidence,
policy and publication approvals remain required before any external mutation.

# Session: v200 current-main external refresh

## Scope

Refresh the non-mutating OSF, Zenodo, source-health, Hugging Face destination and GitHub security
monitors after the security-settings readback improvement merged to `main`.

## Evidence

- Merged commit: `edc29a5`.
- OSF discovery run `29596947892`: passed; no project mutation.
- Zenodo preflight run `29596947909`: passed non-depositing validation; no DOI or deposit.
- Source-health run `29596947921`: passed with no operational blockers; raw payloads remained
  outside tracked storage.
- Hugging Face destination run `29596947958`: failed closed on Space metadata drift
  (`license=mit`, `sdk=gradio` versus governed `apache-2.0`, `static`); no mutation.
- GitHub security-settings run `29596744210`: `blocked_permissions` with the default workflow
  token; the optional read-only `GH_SECURITY_SETTINGS_TOKEN` is not configured.

## Boundary

Operational monitor success does not approve source licences, human research review, policy
claims, OSF registration, Zenodo deposit or Hugging Face publication.

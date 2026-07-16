# v106 blocked-issue criteria synchronization

## Scope

Synchronize the seven remaining blocked GitHub issues with their generated Conductor drafts.

## Evidence

- Issues `#21`, `#23`, `#24`, `#25`, `#26`, `#27` and `#191` remain open.
- Their live bodies now contain the generated, issue-specific acceptance checklists rather than
  the obsolete generic "refine acceptance criteria" template.
- The checklists preserve the blocked boundary: source terms, checksums, permitted fields and
  accountable human review are still required where applicable.
- Issue `#191` explicitly distinguishes provider scanning and repository-owned Gitleaks from the
  unavailable account-level non-provider and validity controls.

## Decision

Do not close or promote any issue based on parser success, local acquisition, or API request
acceptance alone. The GitHub Project and Conductor backlog remain blocked until the corresponding
human, licence, source or account evidence is available.

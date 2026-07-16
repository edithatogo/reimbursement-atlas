# Session v90: external preflight refresh

## Objective

Refresh current external evidence without weakening the repository's fail-closed publication
or source-licence gates.

## Evidence

- Main commit: `e8b8a2edf72740f90a210a5da973b3d221e546ec`.
- OSF workflow `29475141289`: discovery and plan passed; private project `q8cnx` found;
  provisioning and publication skipped; pinned `osf-cli-go` v1.0.0 verified.
- Hugging Face workflow `29475142574`: candidate manifest, research package and dashboard
  validation passed; dataset and Space publication jobs skipped.
- Zenodo workflow `29475143715`: non-depositing preflight passed; no DOI or deposit.
- Source-health workflow `29475144835`: acquisition, source validation, contracts, drift and
  release summary passed; the incomplete-acquisition report retains only the PBS API secret gap.

## Boundary

No OSF, Hugging Face or Zenodo remote mutation was performed. Human licence decisions,
research/protocol approval, evidence-release approval and the PBS subscription credential remain
external gates.

## Merge-protection follow-up

PR #274 exposed a separate queued `zizmor` check from GitHub Advanced Security app `57789`.
The repository-owned SHA-pinned workflow from app `15368` passed. The current authenticated
REST route returned `404 Not Found` when attempting to rebind the required check, so issue #275
records the repository-admin remediation without weakening branch protection.

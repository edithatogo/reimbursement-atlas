# Session: v163 external preflight refresh

Date: 2026-07-17

## Scope

Recheck the current merged main state after the security-monitor merge and keep the OSF and
Hugging Face evidence boundaries current without performing publication mutations.

## Evidence

- Preflight source commit: `c2cdea79206a38692b41df8687f317e8375b5cd5`; the documentation-only
  refresh was subsequently squash-merged to main as `471dab4`.
- OSF workflow run `29565049272` passed pinned `osf-cli-go v1.0.0` discovery and the component
  plan. It found 28 accessible projects, including private project `q8cnx` titled
  `Reimbursement Atlas`; provisioning, registration, upload and publication were skipped.
- Hugging Face destination workflow run `29565126096` reached both public targets. The dataset
  matched its governed `license: other` contract. The Space remained drifted at `license: mit`
  and `sdk: gradio`, versus the candidate `apache-2.0` and `static` values.

## Boundary

No OSF or Hugging Face remote mutation was performed. The repository release gate remains green,
but licence review, evidence and research approval, OSF registration, Hugging Face metadata
reconciliation and policy-claim approval remain explicitly gated.

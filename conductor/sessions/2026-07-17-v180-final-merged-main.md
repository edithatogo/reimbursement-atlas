# v180 final merged-main verification

Date: 2026-07-17
Repository: `edithatogo/reimbursement-atlas`
Merged commit: `8d89c41bb59e414e0c9b5152ff948122a684d020`
Pull request: #427

## Verification

- PR #427 merged through the permitted protected squash workflow after all required checks passed.
- CI, readiness, security, CodeQL, dependency review, zizmor, Scorecard, harness, deterministic
  regeneration and dashboard browser checks passed.
- GitHub Pages run `29579421825` completed build, deploy and HTTPS live smoke successfully.
- Local `main` is clean and synchronized with `origin/main`.
- Handoff v82 bundle and archive checksums verified; raw source payloads are absent from the archive.

## Readiness boundary

`repository_release_ready` is true. `research_publication_ready`, `osf_registration_ready`,
`evidence_release_ready` and `policy_claims_ready` remain false. Open issues for licence review,
source review, research protocols, Hugging Face metadata, Zenodo DOI, account security settings
and TypeScript checker support remain explicitly tracked rather than being represented as passed.

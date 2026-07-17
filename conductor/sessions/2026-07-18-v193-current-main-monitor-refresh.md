# Session v193: current-main monitor refresh

Date: 2026-07-18

## Evidence

Read-only monitors were dispatched against merged `main` commit `8ee60ee`:

- OSF discovery/plan: run `29591535952`, success; provisioning and publication skipped.
- Zenodo preflight: run `29591537888`, success; no DOI or deposit.
- Source health: run `29591540127`, success; six review-only targets, zero operational blockers.
- Hugging Face destination: run `29591542182`, failed closed on Space `mit`/`gradio` drift versus governed `apache-2.0`/`static`; no mutation.
- GitHub security settings: run `29591544121`, `blocked_permissions`; the workflow token cannot read account-level security-analysis settings.

## Repository update

Updated `docs/FINAL_HANDOFF.md`, `docs/RELEASE_READINESS.md` and
`docs/HUGGINGFACE_PUBLICATION.md` with the current commit and monitor IDs. The
documentation preserves the distinction between operational checks and human
licence, research, evidence, policy and publication approval.

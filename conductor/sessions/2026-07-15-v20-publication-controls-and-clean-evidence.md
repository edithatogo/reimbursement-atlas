# Session: v20 publication controls and clean evidence

Date: 2026-07-15

## Completed

- Configured the GitHub `HF_TOKEN` repository secret for the existing dataset and Space targets.
- Ran the Hugging Face workflow with both publication inputs false; candidate build and upload-artifact validation passed, with no remote mutation jobs run.
- Ran the OSF workflow with publication false; the pinned `osf-cli-go v1.0.0-rc.1` install, component-plan generation and fail-closed sync-manifest check passed.
- Ran all seven environment-sensitive gates: pip-audit, npm audit, official Pixi, Pixi installer reachability, zizmor, repo automation and Mojo; all passed.
- Merged PR #157 (`a0fb6bb`) adding fail-closed Hugging Face mutation gates and safer token handling.
- Merged PR #158 (`6550e64`) refreshing generated evidence and removing ignored-cache dependence from committed source-validation outputs.
- Exported and checksum-verified the handoff bundle for `6550e64`.

## Current evidence

- Release readiness: 33/35 pass, 2 warnings, 0 failures, 0 missing gates.
- Repository release readiness: true.
- Research publication, OSF registration, evidence release and policy claims: false.
- No raw files are tracked; ignored `data/raw_live/` remains local-only.
- Public dashboard remains deployed at `https://edithatogo.github.io/reimbursement-atlas/`.

## Remaining blockers

1. Configure `OSF_PROJECT_ID` and obtain a usable OSF authentication context.
2. Complete accountable human licence review for MBS, historical and CMS source families and derived outputs.
3. Complete mapping calibration, methods and cross-platform dashboard review.
4. Acquire or manually review the remaining source payloads, then rerun source validation and contracts.

No remote OSF or Hugging Face publication was performed.

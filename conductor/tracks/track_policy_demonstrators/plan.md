# Implementation plan

- [x] DEMO-01: Generate the three policy demonstrator briefs and summary.
- [x] DEMO-02: Validate fixture/source contracts and typed demonstrator inputs.
- [x] DEMO-03: Validate claim-scope, provenance and limitation boundaries.
- [x] DEMO-04: Synchronize demonstrator issue and Project projections.
- [x] Review Fixes: Keep descriptive demonstrators distinct from evidence
  readiness and publication approval.
- [ ] POL-04: Run all five protocolled analyses on reviewed derived source
  bundles, preserving source versions, permitted fields, transformation
  checksums, denominators, exclusions and sensitivity analyses.
- [ ] POL-05: Produce one immutable claim package per question and complete
  scoped accountable review. Papers and preprints are excluded.
- [ ] POL-06: Regenerate evidence, dashboard and release artefacts after all
  five current packages pass.

## Blocker sequence

The current five packages regenerate deterministically and remain
`pending_accountable_review`. Apply the scoped checksum-bound review decision
before closing POL-05, then regenerate POL-06. See
`docs/POLICY_DEMONSTRATOR_BLOCKER_PLAN.md`.

## Acceptance boundary

The track remains open while any question is below `evidence_ready`. A high
readiness score is not evidence. `data/research_claims/decisions.jsonl` must
bind each approved package to its current SHA-256 and confirm reviewed-derived
inputs, validated analysis and a bounded review record.

## GitHub

- Claim contract: issue #585
- Analysis and review work: issue #586
- Release dependency: issue #532
- Generated issue drafts and Project rows are refreshed by
  `scripts/create_github_project_items.py`.

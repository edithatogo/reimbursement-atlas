# Implementation plan

- [x] POL-01: Generate explicitly caveated parser/rendering fixtures for genomics,
  cognitive/procedural and medicine-opacity routes.
- [x] POL-02: Prevent protocol/linkage scores and fixture outputs from being treated
  as research evidence.
- [x] POL-03: Define and validate the checksum-bound research claim decision contract.
- [ ] POL-04: Run all five protocolled analyses on reviewed derived source bundles,
  preserving source versions, permitted fields, transformation checksums, denominators,
  exclusions and sensitivity analyses.
- [ ] POL-05: Produce one immutable claim package per question and complete scoped
  accountable review. Papers and preprints are excluded.
- [ ] POL-06: Regenerate evidence, dashboard and release artefacts after all five
  current packages pass.

## Acceptance boundary

The track remains open while any question is below `evidence_ready`. A high
readiness score is not evidence. `data/research_claims/decisions.jsonl` must bind
each approved package to its current SHA-256 and confirm reviewed-derived inputs,
validated analysis and a bounded review record.

## GitHub

- Claim contract: issue #585
- Analysis and review work: issue #586
- Release dependency: issue #532
- Generated issue drafts and Project rows are refreshed by
  `scripts/create_github_project_items.py`.

# v100 control and source-status reconciliation

Date: 2026-07-17

## Completed locally

- Added a deterministic first-wave URL/licence checklist generator and focused test.
- Exposed the checklist in the sources dashboard and documented the manual-review boundary.
- Reconciled the Project status calculation so `status:implemented` is exported as `done`
  even when a control retains a `risk:licence` label.
- Reconciled locally implemented controls for the reviewed-source workflow, Hugging Face
  dataset-card gate, checksum-bound licence queue, licence-decision validator, licence queue
  dashboard view, CMS PFS parser prototype, LOINC/HPO/HGNC adapter conventions and source URL
  checklist.
- Converted four previously unlabelled source-validation rows to explicit blocked states.
- Regenerated issue drafts, Project rows, dashboard data, research packaging, data dictionary,
  source drift, seed lake, release readiness and final handoff outputs.

## Verification

- Python 3.14.6 environment.
- 282 tests passed, 2 skipped; total coverage 90.00%.
- Ruff lint and basedpyright typecheck passed.
- Dashboard build passed with 94 pages.
- HF bundle, public-data policy, public docs, citation, seed sync and licence-review validation
  passed.
- Release readiness remains 36/36 passing and repository release-ready.

## Explicit remaining blockers

- CMS CLFS and CMS PFS validation require reviewed local files and source-specific descriptor
  safeguards.
- MBS XML, MBS TXT-pair, PBS monthly-extract and CMS ASP validation require real payload review
  and/or accountable human source-term decisions.
- GitHub non-provider secret-pattern validity scanning remains an account-level control outside
  the repository's local implementation boundary.
- Research/publication/evidence claims remain fail-closed until human review and approved source
  decisions are recorded.

The `deterministic-regeneration` check is implemented as a GitHub workflow context; no local
Pixi task with that name exists. Post-commit regeneration is used locally to verify clean output.

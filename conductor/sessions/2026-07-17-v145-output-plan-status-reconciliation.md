# v145 public output-plan status reconciliation

## Scope

Correct the canonical status of the citation, public dashboard and public status manifest output
plans, then propagate the change through generated Conductor/GitHub artefacts.

## Changes

- Marked `out_citation_cff`, `out_public_dashboard` and `out_public_status_manifest` as
  `implemented` in `data/seed/output_artifact_plans.jsonl` and its CSV mirror.
- Added a regression test requiring these rows to remain implemented while retaining explicit
  fail-closed external approval language.
- Regenerated issue drafts, Project exports, data dictionary, licence-review queue and seed-lake
  outputs.
- Reconciled GitHub issue bodies #347, #348 and #349 with explicit `--apply`; no issue state or
  publication gate was changed.

## Validation

- `pixi run local-quality`: 27/27 gates passed.
- Exact harness deterministic-regeneration sequence: clean diff.
- Focused unit suite: 277 passed.
- `pixi run citation-validate`, `pixi run public-docs`, `pixi run seed-sync-check`, format and
  lint: passed.

## Boundary

Maintainer identity review, source-specific licensing, human evidence/research review, Hugging
Face/OSF/Zenodo publication approval and policy claims remain external gates.

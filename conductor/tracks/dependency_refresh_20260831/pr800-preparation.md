# PR #800 isolated preparation

## Scope and upstream identity

- Remote branch: `dependabot/github_actions/github-actions-a2871219e1`.
- Original remote head: `b921b5eea4e715826460b48bdb84f86091d1bf52`.
- Merged committed main: `9e5d082ed93a50747bcd7c19182691eccf08281a`.
- Local main merge: `f202b1cae7e85a5d30e27b1db3a38233913a7d01`.
- Neither #799's local repair nor #801's uncommitted changes are included.

All four CodeQL references move from
`ff2f1c621b7f889edc0d3c761ac2e6a3f8cdb0dd` (4.37.7) to
`db488ddef3bf6cb639b32c2e9a7c0a7ea8271d28` (4.37.8), in scorecard,
security (init/analyze), and workflow-security. No inputs, permissions, triggers,
or runner settings change. Upstream's action metadata still uses Node 24.

The upstream annotated `v4.37.8` tag object
`37f2634a92ba38a0926ef79a0748ac8ae7d95ab2` resolves to exactly the new commit.
The tag itself is unsigned; GitHub reports the commit signature as valid and
verified. The commit descends from the old SHA (40 commits ahead, zero behind).
[Upstream release notes](https://github.com/github/codeql-action/releases/tag/v4.37.8)
report no user-facing changes. The optional 4.37.9 update is not included.

## Genuine coverage gap

The existing 18 action/workflow tests passed while the separate persisted
`action_pin_resolution.jsonl` still recorded the old CodeQL SHA. Added
`test_codeql_resolution_evidence_matches_current_workflows`, comparing actual
workflow references with that inventory without hardcoding a release SHA or
depending on network access. It failed before regeneration and passed afterward.

Canonical action-pin-resolution generation also reconciles pre-existing line
number, setup-uv pin and workflow-entry drift against committed main. All 119
records are already SHA-pinned (`skipped_sha`); no remote resolution or workflow
rewrite is required. The only source change in the repair is this regression test.

## Execution isolation

Used the existing canonical Python executable read-only after checking relevant
generator/test dependencies against this branch's uv.lock. No environment sync,
install, or update was performed. PYTHONDONTWRITEBYTECODE=1 prevents imported
dependencies from writing bytecode. PYTHONPATH and REIMBURSE_ATLAS_ROOT point to
this worktree; generated outputs and pytest caches stay within it. Raw-cache
links, acquisition jobs, full QA, pushes and PR merges are excluded.

## Commands

Set PYTHON to the validated existing environment executable, then run from the
isolated worktree root:

```sh
export PYTHONDONTWRITEBYTECODE=1 POLARS_MAX_THREADS=2
export PYTHONPATH="$PWD/src" REIMBURSE_ATLAS_ROOT="$PWD"
"$PYTHON" -m pytest -q -n 0 \
  tests/unit/test_automation_v11.py tests/unit/test_action_pins_v12.py \
  tests/unit/test_github_security_workflow_contract.py tests/unit/test_harness_workflow.py
actionlint .github/workflows/scorecard.yml .github/workflows/security.yml \
  .github/workflows/workflow-security.yml
"$PYTHON" scripts/check_action_sha_pins.py
"$PYTHON" scripts/make_repo_automation_matrix.py
"$PYTHON" scripts/resolve_action_pins.py
"$PYTHON" scripts/make_research_package.py
"$PYTHON" -m reimburse_atlas.cli seed-lake data/derived/seed_lake
"$PYTHON" scripts/sync_dashboard_seed.py
"$PYTHON" scripts/make_public_status_manifest.py
```

The task commands from pyproject.toml were then run in the same isolated context
using the existing Python executable directory first on PATH. The harness's
two-pass reconciliation order is:

```text
release-readiness
final-handoff
source-drift
field-lineage
backfill-replay
research-package
seed-lake
dashboard-seed
dashboard-status
zenodo-draft
zenodo-deposition-plan
```

Full QA, actual hosted CodeQL/zizmor execution, and final exact-head checks remain
for the parent after integration. Successful local evidence generation does not
constitute merge approval or publication authorization.

## Validation results

- Existing focused suite: 18 passed.
- New inventory regression: failed on the stale CodeQL SHA before regeneration.
- Focused suite including the new regression: 19 passed.
- actionlint 1.7.12: all three changed workflows passed.
- SHA-pin policy: passed with no violations.
- Ruff lint and format checks: passed for the modified test file.
- Structural inventory check: all 119 resolution rows match the current
  workflow references and line numbers.
- Two canonical receipt-reconciliation passes completed successfully.
- A further repeat of both inventories and the receipt sequence left the
  tracked generated diff byte-identical (SHA-256
  `54c2fb3a6b4d2aada95b96ae1d7e30a3b27ed472a019c3005dad6d88fdf23378`).
- Fresh inventory validation confirms all four CodeQL references use the
  upstream-verified 4.37.8 commit.

The parent subsequently authorized pushing the reviewed repair to trigger CI
while #801 is pending. Neither #799 nor #800 may be merged before #801.

## Sequential strict-base repair

The initial hosted runs 33354886976 and 33354886982 failed generated-artifact
parity, not dependency or security checks. Action-resolution inventory grew from
113 to 119 rows, but the initial scoped sequence omitted `data-dictionary`.
Its two inventory entries and total row count therefore remained stale, cascading
into release gates, research-package hashes, seed-lake and dashboard projections.
The repeated partial sequence above did not establish full regeneration parity.

PR #801 merged as `02116d73da8a8f5dee96009b1ec33691d2704062`, with tested and
merged tree `999415853772673847aed633f6e35f118e0e4204`. PR #799 then passed all
required checks on strict head `c095002986f77aac8ed09ba51f7534559a189b59` and
merged normally as `1f1285847e61e86c9ed5eaa987fc36a3c6508ba4`; its tested and
merged tree was `085b6d1bf948488b6ce4f5a1b733b9215680afd5`.

This branch merges that committed main as
`46f6fa9c9e7420092d89884676194094812204e4`, preserving both plan histories.
Use an isolated `uv sync --locked --all-extras` environment now that the branch
inherits #799's Python updates. Regenerate `repo-automation`,
`action-pin-resolution`, then **`data-dictionary` before** the two downstream
receipt passes listed above. No raw-cache acquisition or unrelated full local
regeneration is needed. Fresh required hosted checks, zero outstanding review
threads and exact-head protected merge remain the delivery gates for this repair.

Strict-base local checks: 23 focused action/workflow/dependency tests passed;
actionlint, SHA-pin policy, and Ruff lint/format passed. The dictionary correction
changes only its two action-resolution entries from 113 to 119 rows; after #801,
the documented total changes from 248632 to 248644. No additional source or test
changes are needed for this projection-only repair.

## Remaining #797 drift

Rechecked official npm latest endpoints during preparation. Main already contains
@astrojs/react 6.0.4. Remaining compatible candidates, not applied here:

- Astro 7.2.4 to 7.2.9: rebuild and browser-test the existing dashboard; keep
  its security overrides and supported Node runtime.
- js-yaml 5.3.0 to 5.4.1: prioritize merge-processing CPU-exhaustion mitigation;
  update the alias pin in both dashboard and vendor-wrapper package.json files.
  Test compatibility because 5.4.0 also changes low-level AST and dump behavior.
- PapaParse 5.6.0 to 5.7.0: low-risk optional remote download timeout addition;
  the current dashboard's text parsing still needs its normal regression checks.
- Cosmograph React 2.3.3 to 2.5.1: React peer constraints admit the installed
  React version, but rendering/annotation changes require browser and graph
  validation; retain the DOMPurify override and accessible fallback.
- TypeScript remains 6.0.3. Version 7 stays excluded until Astro checker support
  and the existing compatibility gate permit it.

Primary references:
[Astro](https://github.com/withastro/astro/releases/tag/astro%407.2.9),
[js-yaml](https://github.com/nodeca/js-yaml/blob/master/CHANGELOG.md),
[PapaParse](https://github.com/mholt/PapaParse/releases/tag/5.7.0),
[Cosmograph](https://cosmograph.app/docs-lib/releases/).

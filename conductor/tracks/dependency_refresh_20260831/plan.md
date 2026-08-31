# Plan

- [x] Review #798, regenerate dashboard SBOM and downstream evidence, validate and merge.
- [ ] Review #799 against updated main, regenerate Python evidence, validate and merge.
- [ ] Review #800 against updated main, regenerate action inventory, validate and merge.
- [ ] Reconcile remaining #797 drift; retain incompatible TypeScript under #362.
- [ ] Renew hosted dashboard/provenance packets under standing scope after the
  dependency baseline settles; do not request fresh owner checksum approvals.
- [ ] Record validation, verify merged trees and clean merged branches before archive.

## Initial diagnosis

PR #798 changes Astro 7.2.3 to 7.2.4 and @astrojs/react 6.0.3 to 6.0.4.
Hosted run 33308373236 reports deterministic SBOM and downstream readiness,
research-package, source-drift and dashboard/seed-lake differences. No application
or security failure is reported by the other completed checks. Regenerate the
canonical evidence, not the approval records by hand.

PR #798 local validation: all 27 native `local-quality` gates passed, including
Python 3.14, coverage, typing, security, package build and dashboard build/audit.
Generated projections are refreshed using the hosted harness sequence. Protected
exact-head hosted checks passed. PR #798 merged as `9e5d082ed93a50747bcd7c19182691eccf08281a`;
tested and merged trees both equal `3013916d2c21b7f8989ea1156a66880df638fc6c`.
The merged local feature branch was removed; #799 and #800 remain separate pending work.

## PR #799 isolated preparation

Prepared from remote head `5c6e95d6e91388cba6586ca151604971f80ef7ab`, merging
committed `origin/main` at `9e5d082ed93a50747bcd7c19182691eccf08281a`.
PR #801 and the canonical checkout's uncommitted changes are not included.

The isolated uv environment installs the locked fastexcel 0.21.0, Hypothesis
6.165.10 and Ruff 0.16.4. Pixi's Ruff pin is aligned to 0.16.4 using
`pixi update ruff --no-install --concurrent-solves 1 --concurrent-downloads 2`;
only Ruff's three platform package records change. Added regression coverage
for uv/Pixi pin parity and a synthetic XLSX parsed through real Polars/fastexcel.

Validation: the initial single-process parser/property/fuzz/projection selection
passed 30 tests; the expanded dependency/live-parser/SBOM/medallion/seed-lake
selection passed 19 tests. Ruff lint/format checks and `uv lock --check` passed.
The isolated installed-environment pip-audit found no known vulnerabilities;
the editable project itself is excluded from that dependency audit.

Regeneration uses the canonical task commands with the isolated `.venv/bin`
first on PATH, worktree-local PYTHONPATH and REIMBURSE_ATLAS_ROOT, and
POLARS_MAX_THREADS=2. Refresh SBOM, medallion projection, research package,
seed lake and dashboard projections, followed by the harness's two-pass
release/handoff/source-drift/field-lineage/backfill/research-package/seed/dashboard/
Zenodo-plan reconciliation. No raw-cache links, downloads or shared-environment
changes are required.

Full local-quality, coverage, dashboard builds, and hosted exact-head checks
are intentionally deferred to the parent after #801 integration to avoid
concurrent full QA jobs. This preparation is not merge approval or a claim
that both complete hosted regeneration workflows have been rerun locally.

Focused validation commands, from the isolated worktree root:

```sh
export PYTHONPATH="$PWD/src" REIMBURSE_ATLAS_ROOT="$PWD" POLARS_MAX_THREADS=2
.venv/bin/python -m pytest -q -n 0 \
  tests/unit/test_dependency_automation_contract.py tests/unit/test_parsers.py \
  tests/unit/test_additional_parsers_v4.py tests/unit/test_first_wave_parsers.py \
  tests/unit/test_live_public_source_parsers.py tests/unit/test_parser_normalise.py \
  tests/unit/test_medallion_projection.py tests/property tests/fuzz
.venv/bin/python -m pytest -q -n 0 \
  tests/unit/test_dependency_automation_contract.py \
  tests/unit/test_live_public_source_parsers.py tests/unit/test_sbom_v11.py \
  tests/unit/test_medallion_projection.py tests/e2e/test_seed_lake_e2e.py
.venv/bin/ruff check .
.venv/bin/ruff format --check .
uv lock --check
.venv/bin/pip-audit --local --skip-editable \
  --cache-dir .venv/pip-audit-cache --progress-spinner off
```

The first pytest result (30 passed) predates the two added regression tests;
the second selection includes them. The audit covers the installed macOS uv
environment, not every platform-specific package in the cross-platform lock.

Both receipt-reconciliation passes completed successfully. A further complete
repeat of SBOM, medallion and the receipt sequence left the tracked generated
diff byte-identical (SHA-256
`c89eced5394dc8a6879000c72540421a1997fc781562cf1895d3610847a26099`).
Both generated SBOM payloads also match a fresh in-memory build from their
respective lockfiles. Final Ruff lint passed and format-check accepted all
1,148 files. No push or PR merge was performed by this preparation pass.

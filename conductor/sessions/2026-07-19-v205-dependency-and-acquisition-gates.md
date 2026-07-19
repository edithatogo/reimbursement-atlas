# Conductor Session v205 - Dependency and Acquisition Gates

Date: 2026-07-19

## Implemented

- Rebuilt the Dependabot Python dependency candidate from current `main`.
- Updated Python/Pixi constraints for PyArrow 25.0.0, Ruff 0.15.22,
  Hypothesis 6.157.0 and Uvicorn 0.51.0.
- Removed the obsolete Uvicorn `standard` extra and regenerated `uv.lock` and
  `pixi.lock`.
- Ran the hardened acquisition plan. Current MBS TXT/XML payloads were
  available locally; PBS used the existing local cache; seven metadata or
  licence-gated targets were skipped by policy.
- Regenerated source-download attempts, source validation, source contracts,
  data quality and final handoff outputs.

## Validation

- `pixi run qa`: 345 passed, 2 skipped, 90% coverage.
- Source acquisition: 3 downloaded, 1 local-cache-available, 7 skipped by
  licence gate.

## Explicit boundary

The dependency and generated-output candidate changes five checksum-bound rows:

1. `data/derived/release_readiness/release_gates.csv`
2. `data/derived/release_readiness/release_gates.jsonl`
3. `data/derived/sbom/cyclonedx-python.json`
4. `data/derived/sbom/sbom_summary.csv`
5. `data/derived/sbom/sbom_summary.jsonl`

These rows remain blocked until explicit repository-owner approval of their
current SHA-256 values. No raw payload, CMS CLFS descriptor, OSF registration,
Hugging Face publication, policy claim or paper was approved or published.

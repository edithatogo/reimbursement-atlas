# Define local adapter contracts for RxNav-in-a-Box style services

Epic: `ONT-001` — Local-only terminology seed workflow

Labels: type:ontology, type:mcp, phase:2-expansion, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`. Refine the acceptance criteria
before opening it in GitHub.

## Acceptance criteria

- [x] Scope is confirmed: a read-only, local-only RxNav-compatible HTTP contract is defined without bundling RxNorm payloads or credentials.
- [x] Licence and data-governance implications are checked: configuration defaults to local use and returned matches remain machine-generated candidates.
- [x] Tests or validation evidence are defined: deterministic URL construction and minimal response parsing are covered by `tests/unit/test_terminologies_v5.py`.
- [x] Documentation or Conductor context is updated in `docs/ONTOLOGY_STRATEGY.md`; domain review is still required before mapping promotion.

# Release readiness

The release-readiness matrix consolidates local quality evidence, security gates, source-data governance, workflow policy, SBOMs, dashboard build status and architecture boundaries.

It is intentionally stricter than a normal CI job: it distinguishes *failed*, *blocked by network*, *missing tool* and *warning* states so a sandbox or local workstation does not falsely claim public-release readiness.

## Command

```bash
PYTHONPATH=src reimbursement-atlas release-readiness --allow-blockers
```

Outputs:

- `data/derived/release_readiness/release_gates.{jsonl,csv}`
- `data/derived/release_readiness/summary.json`

The summary contains `required_blocker_count` and `public_release_ready`. Public release should only proceed when `required_blocker_count == 0`.

## Current blocker pattern

In the current sandbox the local Python, Node, dashboard, SBOM, architecture and public-data gates pass. Remaining blockers are external or advisory:

- `pip-audit --strict` requires network access to the Python advisory database.
- official Pixi is not available in this sandbox.
- `zizmor` correctly flags tag-pinned GitHub Actions until the SHA pin plan is resolved.

These are tracked as evidence rather than hidden in prose.

## Source contract posture

`source_contract_validation_summary` is intentionally advisory until real reviewed-source
downloads are staged in `data/raw_live/` and validated locally. A warning there means the
repo has recorded the parser/contract boundary correctly, not that release readiness is
failing.

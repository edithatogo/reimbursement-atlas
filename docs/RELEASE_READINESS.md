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

The release matrix also verifies that `data/derived/licence_review/summary.json` exists,
contains checksum-bound candidate rows, and explicitly has
`approval_mutation_allowed: false`. This verifies the review-control mechanism only; the
155 candidate rows remain pending until human licence/domain review is recorded.

## Current blocker pattern

As of 2026-07-15, the managed Python 3.14, official Pixi, Node/dashboard,
SBOM, architecture, public-data, action-pinning, CodeQL, dependency-review,
zizmor and branch-protection gates pass. The public GitHub Pages dashboard is
deployed and its machine-readable status contract remains explicitly gated for
research evidence and policy claims.

Remaining blockers are external or require accountable human judgement:

- MBS and historical-source reuse terms require licence review before public
  derived-data publication.
- CMS CLFS/PFS/ASP fields require source-specific licence decisions.
- OSF registration requires an approved protocol freeze; the private `OSF_PROJECT_ID` is now configured;
  `OSF_TOKEN` is configured as a repository secret.
- Hugging Face publication requires the configured `HF_TOKEN` and target repository variables;
  configured, but publication remains disabled until review gates pass.
- Mapping calibration, cross-platform dashboard visual review and policy claims
  require human adjudication.

These states are tracked as evidence rather than hidden in prose.

## Source contract posture

`source_contract_validation_summary` is now expected to pass when the reviewed MBS bundle
is present and landing-page/manual-extract records are intentionally skipped. A warning
there now means a real contract regression, not a placeholder for missing live evidence.

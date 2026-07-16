# CI/CD and repository automation hardening

This repository treats CI/CD configuration as research infrastructure. The reimbursement atlas will ingest public-but-fragile source files, generate derived datasets, and eventually publish artefacts to GitHub and Hugging Face. The automation layer therefore needs to be reproducible, observable and supply-chain aware before live-source ingestion expands.

## Implemented in v11

### Workflow policy matrix

`src/reimburse_atlas/automation.py` scans GitHub Actions workflows and emits dashboard-safe metadata under `data/derived/repo_automation/`:

- `workflow_uses.*` records every `uses:` reference, action ref and pin class.
- `workflow_policy.*` records explicit permissions, checkout credential persistence, action pinning and unsafe trigger checks.
- `automation_controls.*` records higher-level controls such as CodeQL, dependency review, OpenSSF Scorecard, zizmor, artifact attestations, SBOM generation, Renovate, Dependabot and data-publication gates.
- `action_sha_pin_plan.*` is a concrete queue of action references that should be migrated from version tags to full commit SHAs.

Run locally:

```bash
PYTHONPATH=src uv run python scripts/make_repo_automation_matrix.py
```

or through the CLI:

```bash
PYTHONPATH=src uv run reimbursement-atlas repo-automation
```

### SBOM generation

`src/reimburse_atlas/sbom.py` generates minimal CycloneDX 1.6 JSON SBOMs without adding a heavyweight SBOM dependency:

- `data/derived/sbom/cyclonedx-python.json`
- `data/derived/sbom/cyclonedx-dashboard.json`
- `data/derived/sbom/sbom_summary.*`

The Python SBOM is derived from `uv.lock` where available. The dashboard SBOM is derived from `apps/dashboard/package-lock.json`.

Run locally:

```bash
PYTHONPATH=src uv run python scripts/make_sbom.py
```

### GitHub workflow hardening

The workflow layer now includes:

- explicit `permissions:` blocks across workflows;
- `persist-credentials: false` for read-only checkout steps;
- a dedicated `workflow-security.yml` workflow that emits the repo-native workflow policy matrix and runs zizmor as SARIF;
- an `OpenSSF Scorecard` workflow;
- release artefact attestations through `actions/attest`;
- release SBOM attachment and attestation hooks;
- Dependabot cooldown/grouping configuration;
- CI checks for repo automation and SBOM generation.

### Stack canary

`.github/workflows/stack-canary.yml` runs on a weekly schedule and on manual dispatch to
exercise the current-channel stack. It:

- captures optional toolchain and external-quality summaries;
- records dashboard dependency drift in `data/derived/stack_canary/`;
- uses `scripts/make_stack_canary_report.py` to write the reusable summary and issue body;
- uploads the canary summary as a GitHub artifact; and
- opens or updates a single GitHub issue when drift is detected;
- optionally sends a webhook alert when `STACK_CANARY_WEBHOOK_URL` is configured.

### Current status

All workflow action references are pinned to full 40-character commit SHAs and the generated
`action_sha_pin_plan.*` table currently contains no unresolved migrations. `zizmor`, workflow
policy, CodeQL, dependency review, secret-history, reproducible-build and branch-protection
checks are blocking where appropriate. The pin-plan output remains in the repository so future
dependency updates cannot silently reintroduce tag-pinned actions.

The workflow-security check also runs `pixi run action-pin-policy`. This is a fail-closed,
non-mutating policy gate: external actions must use a full 40-character commit SHA, while local
actions and Docker references remain permitted. It does not resolve tags or open pull requests;
dependency updates remain reviewable changes handled by the resolver evidence and normal review.

## Next hardening steps

1. Maintain the pin-plan and fail the generated-artifact gate if a dependency update introduces a tag-pinned action.
2. Preserve human-readable version tags as trailing YAML comments when updating pinned actions.
3. Maintain branch protection requirements as workflows and required-check names evolve.
4. Keep consumer-side attestation verification in the release handoff.
5. Add Hugging Face dataset-card checks before any public derived dataset release.

SHA pinning is intentionally reviewed as a dependency-update operation rather than silently
resolved during ordinary builds. Renovate, `pin-github-action` or a GitHub API-backed bot may
propose updates, but the generated policy gate remains authoritative before merge.

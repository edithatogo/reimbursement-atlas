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
- uploads the canary summary as a GitHub artifact; and
- opens or updates a single GitHub issue when drift is detected.

### Current deliberate non-green signal

`zizmor` is installed and runs. It still reports `unpinned-uses` because workflow actions are pinned to version tags rather than full 40-character commit SHAs. This is recorded as a deliberate hardening backlog rather than hidden. The generated `action_sha_pin_plan.*` table is the migration queue.

## Next hardening steps

1. Resolve every tag-pinned action in `action_sha_pin_plan.csv` to a 40-character commit SHA.
2. Preserve the human-readable version tag as a trailing YAML comment for maintainability.
3. Re-run zizmor and promote it from advisory SARIF to a blocking PR check.
4. Add branch protection rules requiring CI, security, data-smoke, dashboard build and workflow-policy jobs.
5. Add release verification docs showing how consumers can verify GitHub artifact attestations.
6. Add Hugging Face dataset-card checks before any public derived dataset release.

## Why not make SHA pinning automatic here?

This execution environment cannot resolve GitHub DNS from the container, so it cannot safely map every tag to a commit SHA. The repo now produces a deterministic migration queue so that a network-enabled maintainer or CI bot can do the final SHA resolution with Renovate, `pin-github-action`, or GitHub API-backed tooling.

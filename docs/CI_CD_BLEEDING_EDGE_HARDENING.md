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

The workflow-security check also runs `pixi run action-pin-policy`. This is a fail-closed
policy gate: external actions must use a full 40-character commit SHA, while local actions
and Docker references remain permitted. The scheduled
`.github/workflows/action-pin-maintenance.yml` workflow separately resolves all external
refs, refuses partial updates, preserves version comments, and opens a normal reviewable PR
when a complete pin set is available. It never mutates `main` directly; resolver evidence is
uploaded with each run.

The 2026-07-17 stack canary upgraded the compatible dashboard dependencies to Astro `7.1.0`
and `@cosmograph/react` `2.3.3`. TypeScript `7.0.2` was not adopted because the pinned
`@astrojs/check` `0.9.9` peer contract accepts TypeScript 5 or 6; forcing the upgrade with a
legacy peer override would weaken reproducible CI. The follow-up is tracked in the Conductor
backlog and should be re-tested after the checker publishes TypeScript 7 support.

The scheduled `typescript-compatibility.yml` canary now checks that boundary without mutating
`package.json` or the lockfile. It records the checker peer range and TypeScript 7 channel in
`data/derived/toolchain/typescript_compatibility.*`; an upgrade issue is opened or updated only
when the peer contract admits TypeScript 7. Adoption still requires a normal PR with `npm ci`,
Astro check, build and browser validation.

## Next hardening steps

1. Maintain the pin-plan and fail the generated-artifact gate if a dependency update introduces a tag-pinned action.
2. Preserve human-readable version tags as trailing YAML comments when updating pinned actions.
3. Maintain branch protection requirements as workflows and required-check names evolve.
4. Keep consumer-side attestation verification in the release handoff.

Tagged releases now have a read-only preflight job that must pass repository release readiness,
public-data policy, checksum-bound licence-queue validation and immutable action-pin policy before
the build job can create release assets or attestations. This separates release authorization
from the later write-enabled asset upload job.
5. Add Hugging Face dataset-card checks before any public derived dataset release. **Implemented**:
   `scripts/check_huggingface_bundle.py` now requires mixed-data licence metadata, source-specific
   licensing disclosure and an explicit redistribution-permission warning; the data-smoke workflow
   runs this contract on every pull request. This validates the card contract only and does not
   approve source licences or enable publication.

SHA pinning is intentionally reviewed as a dependency-update operation rather than silently
resolved during ordinary builds. The scheduled maintenance workflow is GitHub API-backed and
creates a dedicated branch/PR, while the generated policy gate remains authoritative before
merge. Network or resolver failures fail closed and leave the workflow unchanged.

## Account-bound GitHub security settings

`.github/workflows/github-security-settings.yml` runs a scheduled, read-only `gh api` readback
and uploads `data/derived/repo_automation/github_security_settings.json`. The report records only
the four setting statuses and never includes tokens, request headers or secret values. It keeps
issue #191 synchronized without attempting a repository mutation.

Provider scanning and push protection are the core controls. Non-provider pattern scanning and
partner validity checks are separate advanced controls; when GitHub reports either as disabled,
the monitor uses `blocked_account`, not `pass`. This preserves the account/plan blocker while
keeping the repository's compensating controls visible: Gitleaks history scans, CodeQL, zizmor,
dependency review, pinned Actions and protected-branch checks.

The monitor first uses the optional `GH_SECURITY_SETTINGS_TOKEN` Actions secret, which should be
a fine-grained read-only token scoped only to this repository with `administration:read`, and
falls back to the default `GITHUB_TOKEN` when that secret is not configured. The monitor uses
`blocked_permissions` when the authenticated API response omits the security
analysis object or one of its controls. That state means the token authenticated but cannot
provide authoritative settings visibility; it must not be interpreted as an account-level
disablement. The report includes `missing_controls` and the next action required to rerun with
appropriate read visibility.

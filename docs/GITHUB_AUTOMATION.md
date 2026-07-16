# GitHub automation plan

## Branch protection

Recommended protected branches:

- `main`
- `release/*`

Required checks for `main`:

- CI lint/type/unit/smoke;
- seed-data validation;
- public data policy / raw-cache publication guard;
- security scan;
- dependency review;
- dashboard build once Node dependencies are locked;
- coverage threshold when optional dependencies are available.

The live repository uses a single-maintainer policy: pull-request approvals are not required because
there is no independent collaborator, but all required CI/security/harness checks, administrator
enforcement, linear history, conversation resolution, force-push protection and deletion protection
remain enabled. If a trusted collaborator is added, enable the documented reviewer requirements in
`.github/branch-protection.example.yml` rather than weakening the required checks.

## Issue taxonomy

| Prefix | Meaning |
|---|---|
| `SRC` | Source registry, licence, acquisition or parser work. |
| `MAP` | Crosswalk, ontology or concept-mapping work. |
| `ANA` | Policy analysis design or implementation. |
| `DASH` | Dashboard and graph exploration work. |
| `SEC` | Security, licence and supply-chain work. |
| `DX` | Developer experience, CI, docs and automation. |

## Project fields

- `Phase`: design, slice, expansion, production.
- `Workstream`: conductor, sources, ingestion, mappings, analytics, dashboard, security.
- `Risk`: licence, clinical-review, parser-fragility, dependency, data-quality.
- `Evidence`: none, source-checked, fixture-tested, real-data-tested, clinically-reviewed.
- `Release target`: v0.1, v0.2, v0.3, later.

## Automation candidates

1. Turn `conductor/backlog.yml` into GitHub issues.
2. Apply labels from `.github/labels.yml`.
3. Auto-open parser issues when a source is promoted to first-wave.
4. Generate a data-smoke issue if source URL checks fail.
5. Generate and maintain a source-acquisition issue when scheduled evidence reports
   partial, network-blocked or credential-blocked acquisition targets. This is deliberately
   separate from licence and human-review blockers, which require different decisions.
6. Publish permissive seed-data releases to Hugging Face datasets.
7. Deploy the dashboard Space when graph seed files change on `main`.
8. Fail pull requests that attempt to track ignored raw/local source-cache paths.

The scheduled source-health workflow first runs the hardened source-download attempt with
`PBS_API_SUBSCRIPTION_KEY` injected only from GitHub Actions secrets, then writes the machine-readable
`data/derived/source_health/acquisition_status.json` and the review-friendly Markdown
report beside the validation, contract, drift and release-readiness evidence. Raw downloads
remain on the ephemeral runner and are never uploaded; only derived acquisition, validation,
contract, drift and readiness evidence is retained. The issue is fail-open: missing handoff
evidence, partial acquisition, network blocks and credential blocks keep the issue open;
the issue is closed automatically only when the generated status is `clear`.
The public status manifest and dashboard automation page expose the same report through a
CSV projection, so maintainers can inspect acquisition follow-up without opening CI logs.
When acquisition evidence identifies a missing credential, the report also exposes the
credential's environment-variable name (never its value) in the issue body and dashboard-safe
CSV. This makes a PBS blocker actionable as `PBS_API_SUBSCRIPTION_KEY` without leaking secrets.

## Security posture

- No credentials in `.env.example`.
- Secret scanning and push protection in GitHub repository settings.
- A repository-owned, SHA-pinned Gitleaks history scan runs on pull requests, pushes to `main` and
  a weekly schedule (`.github/workflows/security-assurance.yml`). This is the compensating
  non-provider-pattern control and does not grant GitHub Advanced Security pattern coverage.
- Non-provider secret-pattern scanning is currently an account/security-configuration blocker; the
  live API still reports it as disabled after an enablement attempt. Partner-pattern validity checks
  are a separate control and do not validate generic non-provider patterns; the live API also reports
  them disabled. Do not claim either control is active until the applicable GitHub security settings
  show `enabled`.
- Live verification on 2026-07-16 used the authenticated repository settings API to request
  `enabled` for both `secret_scanning_non_provider_patterns` and
  `secret_scanning_validity_checks`; GitHub accepted the requests but returned `disabled` for both.
  This is retained as an account-level blocker in issue [#191](https://github.com/edithatogo/reimbursement-atlas/issues/191),
  not treated as a repository implementation failure.
- CodeQL for Python and JavaScript/TypeScript.
- Dependabot and Renovate both configured, with Renovate preferred for grouped ecosystem updates.
- SBOM generation and GitHub artifact attestations are implemented in
  `.github/workflows/release.yml`; consumers should follow
  [`docs/RELEASE_VERIFICATION.md`](RELEASE_VERIFICATION.md) to verify checksums and signer
  workflow provenance before installing release artefacts.
- Tagged releases also publish an attested `release-manifest.json` containing the tag, commit,
  relative subject paths, sizes and SHA-256 values for each distribution, source archive and SBOM.
  This is software provenance only and does not authorize Zenodo, OSF, Hugging Face or evidence
  publication.

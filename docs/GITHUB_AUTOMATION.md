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
5. Publish permissive seed-data releases to Hugging Face datasets.
6. Deploy the dashboard Space when graph seed files change on `main`.
7. Fail pull requests that attempt to track ignored raw/local source-cache paths.

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
- CodeQL for Python and JavaScript/TypeScript.
- Dependabot and Renovate both configured, with Renovate preferred for grouped ecosystem updates.
- SBOM and provenance generation to add before package publication.

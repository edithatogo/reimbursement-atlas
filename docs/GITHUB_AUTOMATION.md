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
- CodeQL for Python and JavaScript/TypeScript.
- Dependabot and Renovate both configured, with Renovate preferred for grouped ecosystem updates.
- SBOM and provenance generation to add before package publication.

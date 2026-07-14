# Conductor Workflow

This repository uses a registry-first workflow. The canonical track registry is
`conductor/tracks.yml`; the human status index is `conductor/TRACKS.md`; seed-backed roadmap
functions and generated GitHub issue/project artefacts are the implementation inventory.

## Task Workflow

1. Read the selected track specification and implementation plan.
2. Read project guardrails, `README.md`, `REQUIREMENTS.md`, `DESIGN.md`, the current focus and
   relevant quality gates before editing.
3. Mark the track `[~]` in `conductor/TRACKS.md` before implementation begins.
4. Implement one plan task at a time. Keep raw live data ignored and commit only reviewed derived
   artefacts, metadata, tests, documentation and automation.
5. Add or update tests with every behavioural change. Prefer the narrowest targeted test first.
6. Regenerate all affected seed mirrors, dashboard data, issue drafts, project exports and status
   reports from their canonical sources.
7. Run formatting, lint, type checking, unit/integration/e2e tests, public-data policy checks and
   the dashboard build when the changed surface requires them.
8. Review the diff for secrets, raw payloads, absolute local paths and generated-output drift.
9. Commit cohesive work with a descriptive message, then attach review evidence in a git note when
   the track checkpoint is complete.
10. Keep the track `[~]` while external deployment, licence, human review or publication gates are
    unresolved. Mark `[x]` only when all local acceptance criteria and required external gates are
    satisfied.

## Required Validation

```bash
pixi run citation-validate
pixi run dashboard-status
pixi run format-check
pixi run lint
pixi run typecheck
pixi run test
pixi run public-data-policy
cd apps/dashboard && npm ci && npm run build
```

## External Gates

GitHub Pages deployment, Hugging Face publication, Zenodo DOI creation, OSF registration, source
licence review and human research review are token-, permission- or judgement-dependent. They must
be recorded as blockers and must not be represented as successful local gates.

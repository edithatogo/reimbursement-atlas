# GitHub project plan

## Repository settings

Current configuration:

- `main` branch protection is enabled with 20 required quality, security and harness contexts.
- All required third-party Actions are SHA-pinned; CodeQL, dependency review, Scorecard, actionlint, zizmor and secret-history checks pass.
- Dependabot security updates, secret scanning, push protection and private vulnerability reporting are enabled.
- The repository-owned SHA-pinned Gitleaks history scan runs on pull requests, `main` pushes and a
  weekly schedule as compensating non-provider secret-pattern coverage; it is not equivalent to
  GitHub Advanced Security non-provider pattern scanning.
- GitHub's live API currently reports non-provider secret-pattern scanning and secret-validity checks as
  disabled for this account. An API enablement attempt was fail-closed and did not change the state;
  this remains tracked as a repository-automation/security issue rather than being reported as complete.
  Validity checks are for supported partner patterns, not generic non-provider patterns, so they must
  not be represented as evidence that non-provider scanning is active.
- GitHub Projects v2 is configured as `Reimbursement Atlas Conductor`.
- GitHub Pages workflow deployment is enabled at `https://edithatogo.github.io/reimbursement-atlas/`.
- GitHub Discussions remain disabled because the current project uses Issues and Projects as its review surface.
- GitHub does not currently expose non-provider secret-pattern scanning for this account; this remains an external account-level hardening limitation.

## Project fields

| Field | Values |
|---|---|
| Status | Inbox, Triage, Design, Ready, In progress, Review, Blocked, Done |
| Workstream | Conductor, Sources, Ingestion, Ontologies, Analytics, Dashboard, Security, Docs |
| Phase | 0 Design, 1 Vertical slice, 2 Genomics, 3 Medicines, 4 API/MCP, 5 Atlas |
| Risk | Low, Medium, High |
| Licence impact | None, Review, Restricted |
| Clinical review | Not needed, Needed, Complete |
| Analysis | Link to analysis catalogue id |
| Source | Link to source registry id |

## Issue label taxonomy

- `type:design`
- `type:data-source`
- `type:parser`
- `type:analysis`
- `type:ontology`
- `type:dashboard`
- `type:security`
- `type:ci`
- `risk:licence`
- `risk:comparability`
- `phase:0-design`
- `phase:1-slice`
- `good-first-issue`
- `needs-clinical-review`

## Initial epics

1. Establish Conductor project memory and task map.
2. Validate source registry and source-quality scoring.
3. Build first MBS/CMS parser vertical slice.
4. Implement ontology governance and local-only restricted cache pattern.
5. Render seed graph in Astro/Cosmograph.
6. Add licence-gated Hugging Face dataset publishing.
7. Define first policy paper analysis protocol.

## Idempotent synchronisation

Generated issue drafts remain the deterministic source of truth. Compare them with the live
repository and Project #18 without writing:

```bash
pixi run github-project-sync
```

The command is read-only by default and reports exact-title issue creation and Project-item
actions. Use repeated `--title` filters and explicit `--apply` only after reviewing the plan:

```bash
pixi run github-project-sync --title "Add grouped licence review packet for accountable handoff" --apply
```

The synchroniser never edits, closes, deletes, merges or force-pushes issues and does not print
GitHub credentials. Similar existing issues are reported for human reconciliation rather than
duplicated automatically.

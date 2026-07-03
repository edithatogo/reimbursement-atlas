# GitHub project plan

## Repository settings

Enable:

- branch protection for `main`;
- required status checks: CI, tests, typecheck, security;
- required signed commits if practical;
- Dependabot alerts and security updates;
- secret scanning and push protection;
- CodeQL;
- private vulnerability reporting;
- discussion categories for design, data sources and analyses;
- GitHub Projects v2.

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

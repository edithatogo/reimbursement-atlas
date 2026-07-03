# MCP design placeholder

The repository is not yet an MCP server. This directory records the planned read-only MCP surface so future work can expose the atlas safely.

Initial tools should be read-only:

| Tool | Purpose | Inputs | Output |
|---|---|---|---|
| `atlas.snapshot` | Return source, analysis and readiness counts. | none | JSON summary |
| `atlas.search_sources` | Filter source registry by jurisdiction, domain, access tier or tag. | optional filters | SourceRecord list |
| `atlas.analysis_readiness` | Return bottleneck sources for planned analyses. | optional analysis id | readiness rows |
| `atlas.ingestion_plan` | Return first-wave ingestion plan. | optional source id | IngestionTaskRecord list |
| `atlas.crosswalk_review_queue` | Return generated candidate mappings for local artefacts. | optional threshold | CrosswalkCandidate list |

Write operations, live source fetching and restricted ontology access should remain disabled until the licence and provenance gates are production-ready.

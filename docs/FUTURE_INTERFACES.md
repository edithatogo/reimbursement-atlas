# Future interfaces

## CLI

Planned commands:

```bash
reimbursement-atlas sources
reimbursement-atlas analyses
reimbursement-atlas ingest au_mbs --version 2026-07
reimbursement-atlas map genomics --basket neurodevelopmental
reimbursement-atlas analyse cognitive-vs-procedural
reimbursement-atlas export dashboard
```

## API

A future FastAPI service could expose:

- source registry search;
- schedule item lookup;
- ontology mapping lookup;
- analysis catalogue;
- provenance records;
- graph export;
- semantic search over permitted text.

## MCP server

A future MCP server could allow agents to ask:

- "Find all sources relevant to genomic testing."
- "Show known caveats for Part D/PBS net price comparison."
- "Retrieve mapping candidates for this MBS item."
- "Run the source transparency score."
- "Create GitHub issues for the next Conductor roadmap phase."

## Dashboard

A Hugging Face Space should begin as static and progressively add:

- source registry explorer;
- policy analysis cards;
- graph view;
- schedule comparison vignettes;
- ontology coverage heatmaps;
- provenance and licence badges.

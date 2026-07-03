# Roadmap

## Phase 0: Design maturity — substantially complete

- Conductor context layer.
- Requirements and architecture.
- Source registry with 60 public/partly public source families.
- Analysis catalogue with 25 policy analysis concepts.
- Ontology strategy and licence-risk conventions.
- GitHub automation plan.
- Dashboard skeleton.
- Seed graph.

## Phase 1: First executable vertical slice — in progress

Completed in the current local prototype:

- fixture-backed MBS XML-like parser to `ScheduleItemRecord`;
- fixture-backed CMS CLFS-like CSV parser to `ScheduleItemRecord`;
- fixture-backed NHS genomic-directory-like CSV parser to `CoverageDecisionRecord`;
- source and analysis readiness tables;
- first-wave ingestion-plan table with network and licence gates;
- deterministic token-overlap crosswalk review queue;
- dashboard-safe CSV sync into Astro/Cosmograph app;
- optional read-only API and MCP design scaffolds;
- 36 local tests passing with optional integration/property tests skipped if dependencies are absent.

Next:

1. validate parser assumptions against one manually downloaded MBS XML release;
2. validate CMS CLFS CSV column variants while avoiding restricted CPT long-descriptor redistribution;
3. validate NHS genomic-directory workbook/CSV shape;
4. build a tiny live-source provenance manifest with checksums and effective dates;
5. add Polars/DuckDB materialisation for parsed records and crosswalk queues;
6. add dashboard tables for readiness and ingestion plans;
7. open GitHub issues from the generated backlog.

## Phase 2: Genomics demonstrator

- Genomic/pathology test basket.
- LOINC/HPO/HGNC mapping workflow using local or permissively redistributable sources only.
- CMS LCD/NCD and MSAC text-retrieval strategy.
- Coverage timeline.
- Uptake/diffusion analysis using available aggregate utilisation.
- Policy brief and dashboard.

## Phase 3: Medicines demonstrator

- PBS/PBAC, CMS ASP/Part B, NHS Drug Tariff, PHARMAC and Japan NHI drug examples.
- ATC/RxNorm mapping.
- RxNav-in-a-Box compatible local service conventions.
- Restriction-text extraction.
- Published-versus-effective price opacity index.

## Phase 4: Interface expansion

- CLI stabilisation.
- Read-only local API.
- Read-only MCP server.
- Hugging Face dataset publication for permissive generated artefacts.
- Hugging Face Space dashboard deployment.

## Phase 5: Production hardening

- Live-source acquisition with explicit provenance and licence gates.
- Versioned source snapshots.
- SBOM/SLSA release evidence.
- Mutation testing thresholds.
- Security policy and dependency-management enforcement.
- Human clinical/economic review workflow for crosswalks and policy outputs.

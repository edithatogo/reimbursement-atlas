# Session: v17 evidence readiness, source drift and data dictionary

## Focus
Implemented the next governance/evidence layer after v16: research-question evidence readiness, source/schema drift reporting, and a public artefact data dictionary.

## Implemented
- `EvidenceReadinessRecord`, CLI command and generated outputs.
- `SourceDriftRecord`, CLI command and generated outputs.
- `DataDictionaryRecord`, CLI command and generated outputs.
- Detailed OSF-style protocol and report scaffolds for all five research questions.
- Dashboard tables for evidence readiness, source/schema drift and data dictionary.
- Release-readiness and local-quality gate integration.
- Conductor roadmap functions, output artefact plans and issue-draft coverage.

## Current state
All five research questions are now `prototype_ready` in the generated evidence-readiness matrix, but none are `evidence_ready` because real reviewed-source bundles and human preregistration review are still outstanding.

## Next recommended work
Run live source downloads in a network-enabled environment, create reviewed MBS/PBS/CMS bundles, then promote at least the source-transparency and genomics/pathology questions toward evidence-ready status after mapping review.

# ADR 0029: Evidence readiness, source drift and data dictionary as release gates

## Status
Accepted.

## Context
The repository had source validation, data quality, protocols and research linkages, but no single generated view showing whether a research question was ready for prototype/policy analysis. It also lacked a reusable source/schema drift report and a public artefact data dictionary suitable for Hugging Face, OSF and release review.

## Decision
Add three generated artefact families:

1. evidence-readiness rows for each protocolled research question;
2. source/schema drift rows for paired tabular artefacts and future source-version comparisons;
3. a public artefact data dictionary for candidate release files.

All three are exposed through the CLI, Pixi tasks, local-quality gates, release-readiness gates, dashboard CSVs, publication manifest and Conductor/GitHub issue generation.

## Consequences
Research questions now have visible prototype/evidence readiness. Schema drift is reviewable before release. Dataset consumers can inspect a generated data dictionary before downloading release artefacts. Real-source ingestion remains required before evidence-ready policy claims are allowed.

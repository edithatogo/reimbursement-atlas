# Report scaffold: genomics and pathology reimbursement architecture

## Current status
This report is not yet a results paper. It is a structured analysis scaffold linked to the OSF protocol, Conductor tracks, source-download plan, data-quality checks, evidence-readiness rows and GitHub issue backlog. No policy conclusion should be drawn until real reviewed-source bundles are generated and the mapping review workflow is complete.

## Research question
How do public systems connect genomic/pathology test coverage, price and eligibility restrictions?

## Evidence available now
The bounded package `data/derived/research_claims/rq_genomics_coverage_price.json`
records reviewed MBS evidence and the validated genomics mapping stratum. CMS CLFS,
CMS MCD and the UK Genomic Test Directory remain absent as reviewed bundles, so no
cross-system coverage-price conclusion is supported.

Missing jurisdictions are exclusions, not zero observations. Their absence must
remain visible in every denominator, table, dashboard summary and interpretation.

## Minimum evidence required before interpretation
A release candidate for this question requires: reviewed source snapshots; derived-only parsed records; source-content validation; data-quality pass; data dictionary; source/schema drift report; candidate mappings; human review of policy-facing mappings; sensitivity analyses; and publication-manifest review. Any restricted terminology or confidential price concept must remain local-only or be represented as metadata.

## Planned results sections
The results report should include source inventory, inclusion flow, mapping review summary, main policy metrics, sensitivity analyses, limitations, reproducibility statement, OSF/Hugging Face/Zenodo artefact links and a plain-language policy interpretation.

## Reviewer checklist
Reviewers should confirm that the unit of comparison is valid, source licence gates are respected, raw descriptors are not leaked, patient-cost claims are supported, coverage and payment are not conflated, and uncertainty is visible in every policy-facing table.

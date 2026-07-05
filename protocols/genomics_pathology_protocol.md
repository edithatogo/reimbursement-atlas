# Protocol: genomics and pathology reimbursement architecture

## Question
How do public systems connect genomic/pathology test coverage, price and eligibility restrictions?

## Core systems
Australia MBS, US CMS CLFS and Medicare Coverage Database, England NHS Genomic Test Directory, and selected international comparators after source validation.

## Primary outcomes
- Whether a test has an explicit fee/reimbursement record.
- Whether coverage is national, local, conditional or unclear.
- Restriction/eligibility wording category.
- Price concept, currency, effective date and facility/professional bundling caveat.
- Mapping confidence and reviewer status.

## Methods
1. Ingest derived-only schedule records.
2. Link coverage records without treating payment-file presence as coverage.
3. Generate candidate mappings using deterministic lexical/vector evidence.
4. Require human adjudication for policy-facing mappings.
5. Produce coverage-price-restriction matrices and sensitivity analyses.

## Exclusions
Raw restricted descriptors, copyrighted CPT text, confidential net prices and unreviewed ontology dumps are not public outputs.

## OSF outputs
Protocol, mapping appendix, analysis report and data dictionary.

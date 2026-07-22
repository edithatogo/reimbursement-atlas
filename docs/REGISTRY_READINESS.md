# Registry Readiness Contract

Status: `repository_ready_external_gates_pending`

Roadmap: `research_database_registry_readiness_20260721`

- Parent issue: [#530](https://github.com/edithatogo/reimbursement-atlas/issues/530)
- Licensing and release metadata: [#531](https://github.com/edithatogo/reimbursement-atlas/issues/531)
- Zenodo/DataCite: [#532](https://github.com/edithatogo/reimbursement-atlas/issues/532)
- FAIRsharing eligibility: [#533](https://github.com/edithatogo/reimbursement-atlas/issues/533)
- Hugging Face/Croissant: [#534](https://github.com/edithatogo/reimbursement-atlas/issues/534)

## Current contract

Software and project-owned documentation use Apache-2.0. Underlying source data retain provider licences and are never relicensed by the repository. The generated publication manifest and release-readiness artefacts are the canonical repository-side evidence for any future dataset publication.

Hugging Face and Zenodo publication workflows are manual, token-gated, and approval-gated. FAIRsharing remains conditional on a mature searchable research database and an appropriate record type. Local readiness does not establish a DOI, public dataset, curator decision, or policy evidence.

## Required evidence

- Licence and source-provenance decisions are attached to each source family.
- Release metadata, checksums, and generated manifests are internally consistent.
- Dataset-card/Croissant metadata is derived from the governed publication candidate.
- Any external publication records the exact release revision and authoritative identifier.

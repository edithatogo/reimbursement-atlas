# FAIRsharing Eligibility Assessment

This is a repository-local assessment record, not a FAIRsharing submission or
eligibility decision. It defines the evidence required before the project is
considered for a searchable FAIRsharing record.

## Current Status

**Assessment complete; submission deferred because the public product is not yet a mature
searchable research database.** On 2026-07-22 the project name and repository identity were
searched against FAIRsharing-facing web results, and the official database-record guidance was
reviewed. No existing Reimbursement Atlas record was identified. FAIRsharing database records
describe maintained resources and require database-level metadata such as identifier schemes;
the current product is a static, prototype-grade dashboard whose evidence and policy gates remain
closed. Creating a record now would overstate maturity.

Authoritative guidance reviewed:

- <https://fairsharing.gitbook.io/fairsharing/how-to/searching-and-browsing/search>
- <https://fairsharing.gitbook.io/fairsharing/associated-records/from-database-records>
- <https://fairsharing.gitbook.io/fairsharing/programmatic-access/fairsharing-rest-api>

## Assessment Criteria

| Criterion | Local evidence | Current status |
|---|---|---|
| Stable project identity | GitHub repository, `CITATION.cff`, registry metadata | Prepared |
| Maintained documentation | README, data model, provenance and transformation documentation | Prepared |
| Machine-readable metadata | publication manifest, data dictionary, Frictionless, DCAT, RO-Crate and Croissant candidates | Prepared |
| Persistent release identity | tagged release manifest and GitHub attestations | Prepared; no DOI minted |
| Data and software rights | Apache-2.0 code boundary plus source-specific licence matrix and checksum queue | Prepared; human review remains |
| Searchable FAIRsharing eligibility | Search and database-record guidance reviewed 2026-07-22 | Deferred: product maturity and evidence gates are insufficient |
| Submission or acceptance | authoritative FAIRsharing record URL/identifier | Not submitted; no submission authorised or warranted |

## Required External Evidence

Before reconsidering submission, record:

1. the FAIRsharing search date and query;
2. the applicable record type and eligibility rationale;
3. any duplicate or related records and their identifiers;
4. the submitted record URL and identifier, if submission is authorised; and
5. the acceptance, rejection or requested-changes evidence from FAIRsharing.

Reassess only after a stable DOI-backed release, a maintained searchable/API service, closed
evidence gates, and a documented identifier scheme exist. Local metadata preparation, a passing
CI run, or a GitHub repository does not substitute for that external evidence. Do not upload
restricted source payloads, credentials or unreviewed derived data as part of an eligibility
assessment.

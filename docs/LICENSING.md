# Licensing

## Repository code and documentation

The original code, documentation, schemas, tests, and repository automation
written for Reimbursement Atlas Conductor are licensed under the Apache License
2.0. See [`LICENSE`](../LICENSE) and the SPDX identifier `Apache-2.0`.

Apache-2.0 applies only to material the project contributors own or are
authorized to license. It does not relicense external source data, source
descriptors, ontologies, trademarks, or third-party documentation.

## Source data

Every external source is governed by its own terms. The repository owner has
approved the current checksum-bound derived/metadata licence scope. Source
records continue to carry source-specific attribution and restrictions; this
approval does not relicense provider data or permit raw-payload redistribution.
Examples include:

- Australian MBS and PBS materials: retain Commonwealth or publisher terms and
  retain the approved downstream scope when publishing derived fields. The current
  MBS Online copyright notice permits limited personal, non-commercial, unaltered
  use and requires written approval for redistribution; see
  [`SOURCE_LICENCE_EVIDENCE.md`](SOURCE_LICENCE_EVIDENCE.md).
- CMS CLFS/PFS materials: use the applicable CMS/AMA source licence and terms,
  including attribution and any field-level restrictions. Apache-2.0 does not
  override those terms. CPT descriptors and other licence-gated payloads are
  excluded unless the applicable CMS/AMA permission expressly allows them.
- External ontologies and terminology services: use only the permitted local,
  API, or derived representation for that resource.

## Derived outputs

Derived tables are not automatically Apache-2.0. A derived output may be
published only when its source-specific manifest row records attribution, the
approved scope, evidence of licence review, and any required
restrictions. Otherwise it remains local or metadata-only. The publication
manifest, public-data policy, source-contract, evidence-readiness, and
release-readiness gates are authoritative for each output. The grouped questions in
[`LICENCE_DECISION_MATRIX.md`](LICENCE_DECISION_MATRIX.md) simplify review but never
replace the checksum-bound row-level decision record.

Hugging Face, OSF, Zenodo, and preprint publication workflows must preserve
these per-artifact terms and must fail closed when a source gate is unresolved.

The project decision is therefore: Apache-2.0 for project-owned code and
documentation; the originating provider's licence for external data and
provider-owned derived content.

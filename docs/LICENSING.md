# Licensing

## Repository code and documentation

The original code, documentation, schemas, tests, and repository automation
written for Reimbursement Atlas Conductor are licensed under the Apache License
2.0. See [`LICENSE`](../LICENSE) and the SPDX identifier `Apache-2.0`.

Apache-2.0 applies only to material the project contributors own or are
authorized to license. It does not relicense external source data, source
descriptors, ontologies, trademarks, or third-party documentation.

## Source data

Every external source is governed by its own terms. Source records therefore
carry source-specific licence gates and attribution notes. Examples include:

- Australian MBS and PBS materials: retain Commonwealth or publisher terms and
  confirm downstream redistribution before publishing derived fields.
- CMS CLFS/PFS materials: retain AMA/CMS restrictions and do not redistribute
  CPT descriptors or licence-gated payloads.
- External ontologies and terminology services: use only the permitted local,
  API, or derived representation for that resource.

## Derived outputs

Derived tables are not automatically Apache-2.0. A derived output may be
published only when its source-specific manifest row records attribution,
redistribution permission, evidence of licence review, and any required
restrictions. Otherwise it remains local or metadata-only. The publication
manifest, public-data policy, source-contract, evidence-readiness, and
release-readiness gates are authoritative for each output.

Hugging Face, OSF, Zenodo, and preprint publication workflows must preserve
these per-artifact terms and must fail closed when a source gate is unresolved.

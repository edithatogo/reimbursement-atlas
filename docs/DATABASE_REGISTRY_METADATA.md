# Database Registry Metadata

This record is the repository-local metadata handoff for database, archival and
research-software registries. It is suitable as a source for a later Zenodo,
DataCite or institutional repository deposit, but it is not evidence that a
deposit has been submitted or accepted.

## Identity

- **Title:** Reimbursement Atlas Conductor
- **Repository:** <https://github.com/edithatogo/reimbursement-atlas>
- **Software licence:** Apache-2.0 for project-owned code and documentation; see
  [`LICENSE`](../LICENSE).
- **Citation metadata:** [`CITATION.cff`](../CITATION.cff).
- **Release subject manifest:** generated at `data/derived/release_manifest.json`
  for a tagged release.

## Data Rights

The repository contains project-owned software plus candidate derived and
metadata artefacts. Underlying MBS, PBS, CMS, ontology and other provider terms
remain authoritative and are not relicensed by Apache-2.0. Exact candidate
paths, checksums, scope, attribution and redistribution decisions are recorded
in the generated licence queue and companion ledger:

- `data/derived/publication_manifest.json`
- `data/derived/licence_review/licence_review_queue.jsonl`
- `data/licence_review/decisions.jsonl`
- [`docs/LICENSING.md`](LICENSING.md)
- [`docs/SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md`](SOURCE_PROVENANCE_AND_TRANSFORMATIONS.md)

Raw live-source payloads, restricted descriptors, credentials and confidential
values are excluded from public registry packages by policy.

## Reproducibility

```bash
pixi run publication-manifest
pixi run research-package
pixi run licence-review-validate
pixi run release-readiness
pixi run sbom
```

Tagged software releases additionally publish a checksum-bearing manifest and
GitHub artifact attestations. See [`docs/SBOM_AND_PROVENANCE.md`](SBOM_AND_PROVENANCE.md)
and [`docs/RELEASE_VERIFICATION.md`](RELEASE_VERIFICATION.md).

## Registry Status

| Destination | Local preparation | External submission or acceptance |
|---|---|---|
| GitHub repository | Active and version-controlled | Repository exists; release tags remain governed |
| OSF | Protocol/report scaffolds available | Registration/public record pending explicit gates |
| Hugging Face | Dataset card, Croissant descriptor and static Space metadata available | Publication pending licence, evidence and policy gates |
| Zenodo/DataCite | Release metadata and manifest scaffolds available | DOI/deposit not submitted |
| FAIRsharing | Eligibility assessment record available | Search, record type and submission/acceptance pending |

This status must be updated only from authoritative external evidence. Local
validation, a green workflow or a prepared metadata file does not imply
eligibility, submission, acceptance or publication.

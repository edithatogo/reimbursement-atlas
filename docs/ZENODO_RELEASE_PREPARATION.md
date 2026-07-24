# Zenodo release preparation

This document describes a local preflight contract, not a current external deposition state.
Regenerate the preflight against the exact tagged release; no Zenodo evidence is implied for a
newer commit.

The current merged-main baseline is
`b2b4cdf0f2488cb2ef2eea83f0e2f47bdd46a1b1`. No Zenodo deposit has been
authorized. The exact tagged release must regenerate and revalidate the inventory
after OSF registration and research-evidence gates pass.

The repository contains `.zenodo.json` as a locally validated metadata preparation record. It
does not create a Zenodo record, reserve a DOI, upload source files or imply archival/publication
approval.

Validate it without network access:

```bash
pixi run zenodo-metadata
```

Before deposition, an accountable maintainer must confirm:

1. reviewed-source and source-contract gates are complete;
2. the software and every derived artefact have the correct licence treatment;
3. OSF protocol and research review are approved;
4. the exact tagged release, SBOMs, checksums and GitHub attestations are frozen; and
5. the Zenodo target, creators, description and related identifiers are correct.

The frozen release inventory is fail-closed and requires a wheel, sdist, tagged source archive,
Python and dashboard SBOMs, release manifest and machine-readable attestation receipts. Every row
records its role, filename, byte size, SHA-256 and Zenodo-compatible MD5 checksum. Missing roles or
checksum drift block draft creation, DOI reservation and publication.

The tagged GitHub release publishes the machine-readable receipts emitted by
`gh attestation verify --format json`. Every remote Zenodo transition requires the exact GitHub
release tag, downloads that tag's assets, reconstructs the inventory paths, and verifies each
subject against its receipt, signer workflow and tag ref before generating deposition inputs.
This prevents a source-only workflow checkout from being mistaken for a frozen release payload.

Preflight wording is retained only in `preflight.json`. The final Zenodo and DataCite metadata
must describe the release itself and must not claim that it is merely a preparation record.
DataCite validation requires named ORCID-bearing creators, explicit software and derived-data
rights, typed related identifiers, an explicit funding array (empty means no funding was
declared), temporal coverage and geographic coverage.

Only then may a token-gated Zenodo workflow be enabled. The current release-readiness summary
must continue to report `research_publication_ready: false` and no DOI until that decision is
recorded.

The manual `.github/workflows/zenodo-preflight.yml` workflow now validates the metadata and
repository gates and emits a non-depositing preflight artifact. It has read-only permissions,
does not accept a token and cannot create a DOI; a future deposition workflow requires a
separately approved Zenodo environment and accountable publication authorization.

## Token-gated deposition workflow

The `Zenodo preflight` workflow now separates five transitions:

- `plan` regenerates metadata and evaluates upstream gates without credentials or mutation.
- `draft` creates an unpublished deposit and uploads the frozen inventory only after every
  archive gate passes, the `CREATE_ZENODO_DRAFT` confirmation and `zenodo-production` environment
  approval.
- `reserve` adds `prereserve_doi` only after every archive-publication gate passes and the exact
  `RESERVE_ZENODO_DOI` confirmation is supplied.
- `publish` is irreversible and requires every gate plus `PUBLISH_ZENODO_RECORD`.
- `verify` reads the remote deposition state and records the DOI, record URL and filename,
  byte-size and checksum parity for every frozen release asset. For a published record it also
  resolves the version DOI without credentials, queries DataCite, verifies title, creator ORCID,
  publisher, version and software resource type, and records concept and version DOIs separately.

Both `reserve` and `publish` first read the unpublished draft and require complete remote file and
publication-critical metadata parity. Publication additionally requires a non-empty reserved
version DOI. A mismatch fails before the irreversible publish action.

For every mode except `plan`, set `release_tag` to the exact published GitHub release tag. The
workflow rejects an empty tag, a tag that does not equal the package version, missing release
assets, missing attestation receipts, receipt verification failure and inventory drift before it
reads the Zenodo token.

`scripts/zenodo_deposition.py` sends bearer credentials only to
`https://zenodo.org/api` or `https://sandbox.zenodo.org/api`; redirects to arbitrary API hosts are
rejected before a token is read. The implementation follows the official
[Zenodo deposit API](https://developers.zenodo.org/), including bucket uploads and the explicit
publish action. The generated `external_state.json` is redacted and never contains a token.

The current repository remains in `plan` state. The workflow must not create a draft, reserve or
publish a DOI
until mapping adjudication, the one-time holdout, scoped dashboard review, OSF registration,
licensing and release-readiness independently pass.

The tagged GitHub release workflow also performs a separate read-only governance preflight before
building or attesting assets. It does not approve research publication or Zenodo deposition; it
only prevents release automation from bypassing repository, evidence, OSF registration, policy,
licence-queue and action-integrity gates. The preflight invokes the same fail-closed
`archive-publication-gate` predicate used by Zenodo mutation modes; regenerating a readiness report
that still contains blocked gates is not sufficient.

# Zenodo release preparation

Release snapshot described by this preflight is
`578760f1647c01f11caaf5e1a7f7bf6d38129dea` (2026-07-22). Regenerate this preflight after any
further merge; no Zenodo evidence is implied for a newer commit.
The latest merged-main preflight is run `29595536320`. Metadata and
repository-readiness validation passed; no DOI was created and no Zenodo deposit
or external mutation occurred. Deposition remains gated on human licence,
research and publication approval.

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
- `draft` creates an unpublished deposit and uploads the frozen inventory only after the
  `CREATE_ZENODO_DRAFT` confirmation and `zenodo-production` environment approval.
- `reserve` adds `prereserve_doi` only after every archive-publication gate passes and the exact
  `RESERVE_ZENODO_DOI` confirmation is supplied.
- `publish` is irreversible and requires every gate plus `PUBLISH_ZENODO_RECORD`.
- `verify` reads the remote deposition state and records the DOI, record URL and remote file count.

`scripts/zenodo_deposition.py` sends bearer credentials only to
`https://zenodo.org/api` or `https://sandbox.zenodo.org/api`; redirects to arbitrary API hosts are
rejected before a token is read. The implementation follows the official
[Zenodo deposit API](https://developers.zenodo.org/), including bucket uploads and the explicit
publish action. The generated `external_state.json` is redacted and never contains a token.

The current repository remains in `plan` state. The workflow must not reserve or publish a DOI
until mapping adjudication, the one-time holdout, scoped dashboard review, OSF registration,
licensing and release-readiness independently pass.

The non-depositing preflight was rerun successfully as
[workflow run 29569972301](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29569972301)
on merged `main` commit `fc47649` (the latest non-mutating preflight; the current repository
commit is `db367f4`).
Its artifact records `mutation_performed: false`, `doi_created: false` and
`human_publication_approval_required: true`.

The latest current-main non-depositing preflight is
[29571894944](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29571894944).
It passed metadata and repository-readiness validation and recorded
`mutation_performed: false`, `doi_created: false` and
`human_publication_approval_required: true`.

The tagged GitHub release workflow also performs a separate read-only governance preflight before
building or attesting assets. It does not approve research publication or Zenodo deposition; it
only prevents software release automation from bypassing repository, policy, licence-queue and
action-integrity gates.

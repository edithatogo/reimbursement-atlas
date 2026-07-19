# Zenodo release preparation

Release snapshot described by this preflight is
`89127e48ba0035a330aafa950c1bed0476ad0077` (2026-07-19). Regenerate this preflight after any
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

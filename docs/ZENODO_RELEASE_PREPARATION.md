# Zenodo release preparation

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

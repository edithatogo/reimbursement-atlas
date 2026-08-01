# Research-data packaging standards

## Scope

Generate and validate release-candidate metadata for permitted derived outputs
using Frictionless Data Package, RO-Crate, DCAT JSON-LD and repository citation
metadata. Raw restricted source payloads, credentials, papers and preprints are
outside scope.

## Acceptance criteria

- `datapackage.json`, `ro-crate-metadata.json` and `dcat.jsonld` are generated
  deterministically from the governed publication manifest.
- Descriptor resources contain only permitted relative paths and valid JSON or
  JSON-LD structures; no raw or local absolute paths are included.
- Citation and licensing boundaries distinguish Apache-2.0 software from
  source-specific derived-data terms.
- Regeneration is byte-stable and validated by the repository test suite.
- Zenodo DOI creation remains a separate externally gated release action.

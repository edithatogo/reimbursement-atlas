# Session v150: Zenodo metadata lifecycle

## Objective

Reconcile the locally implemented Zenodo metadata/preflight surface with the
external DOI publication plan without enabling a remote mutation.

## Changes

- Marked `out_zenodo` as `implemented` with an explicit non-depositing note.
- Kept `out_zenodo_release_doi` as `planned` behind human publication approval.
- Added a contract test covering the metadata/DOI status split.
- Regenerated seed mirrors, GitHub issue/project rows, package metadata,
  source-drift, data-quality, release-readiness and dashboard seed outputs.
- Reconciled GitHub issue #121 after generation.

## Validation boundary

`pixi run zenodo-metadata` passes. No Zenodo credentials, record, upload or DOI
was used. Research, licence, governance and publication gates remain fail-closed.

# v29 research-package determinism

## Scope

Fix self-referential checksums in the Frictionless, RO-Crate and DCAT descriptors.

## Implementation

- Filter the three descriptor paths from the manifest used to generate them.
- Preserve the frozen `PublicationManifest` contract with `dataclasses.replace`.
- Add a two-run byte-identity regression test.
- Add the packaging hardening item to `conductor/backlog.yml` and roadmap seed data.
- Regenerate issue drafts, Project rows, data dictionary, release readiness, seed lake,
  dashboard seed and research-package outputs.

## Evidence

- `10 passed` in `tests/unit/test_v14_roadmap_downloads_osf.py`.
- Consecutive generation checksums match for `datapackage.json`, `ro-crate-metadata.json`
  and `dcat.jsonld`.
- Release-readiness remains `35/35` passing and software-release ready only.
- Human licence, mapping, OSF, HF and policy gates remain fail-closed.

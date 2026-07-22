# Implementation plan

- [x] OSF-01: Populate title, description, contributor, licence, subjects and tags in the draft. (Issue #484, subissue #488)
- [x] OSF-02: Map each research question to protocol, source, transformation and output artefacts. (Subissue #488)
- [x] OSF-03: Freeze source cutoff and validate manifest/dictionary/RO-Crate parity. (Subissue #489)
- [x] OSF-04: Export redacted draft metadata and run OSF CLI validation. (Subissue #489)
- [ ] OSF-05: Human review checkpoint: decide whether to submit the registration; do not submit papers. (Subissue #511)

## Validation

- `osf validate <draft-or-registration> --profile preregistration`
- `pixi run osf-cli-contract`
- `pixi run research-package`
- `pixi run release-readiness`

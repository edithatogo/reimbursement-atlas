# Implementation plan

- [x] OSF-01: Populate title, description, contributor, licence, subjects and tags in the draft. (Issue #484, subissue #488)
- [x] OSF-02: Map each research question to protocol, source, transformation and output artefacts. (Subissue #488)
- [x] OSF-03: Freeze source cutoff and validate manifest/dictionary/RO-Crate parity. (Subissue #489)
- [x] OSF-04: Export redacted draft metadata and run OSF CLI validation. (Subissue #489)
- [x] OSF-05: Human review checkpoint: the accountable owner approved the checksum-bound
  registration freeze and 11 exact repository/protocol/report artefacts. The approved protocol
  digest is `d16aced4316d57a5e0e965707769142fc5c7a8c37461257c9884b019f11f2555`;
  the approved manifest digest is
  `e2d87ba924cbd01b8954d45c66ddd28d88c17ff3746aea1a91de616445230678`;
  the source cutoff is `2026-07-23T00:00:00Z`. Papers, preprints, raw payloads and restricted
  descriptors remain excluded. (Subissue #511)

## Validation

- `osf validate <draft-or-registration> --profile preregistration`
- `pixi run osf-cli-contract`
- `pixi run research-package`
- `pixi run release-readiness`

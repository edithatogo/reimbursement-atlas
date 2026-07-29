# Create the approved Zenodo draft from the exact tagged release

Epic: `RAC-PUBLISH-001` — External publication and archive execution

Labels: type:publication, type:release, type:zenodo, status:blocked

Status: `blocked`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [ ] The v0.1.0 GitHub release assets, SBOMs, manifest and attestations are downloaded and checksum-verified.
- [ ] The Zenodo draft is created only with CREATE_ZENODO_DRAFT and never published by this task.
- [ ] The redacted external-state receipt records the deposition identifier and asset parity, or the exact API blocker.
- [ ] Papers, manuscripts and preprints are excluded.

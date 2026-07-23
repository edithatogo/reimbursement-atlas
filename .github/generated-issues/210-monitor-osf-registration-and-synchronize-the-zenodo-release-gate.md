# Monitor OSF registration and synchronize the Zenodo release gate

Epic: `RAC-RELEASE-001` — Citation, archive and public record maturity

Labels: type:automation, type:osf, type:release, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] A scheduled read-only monitor records the OSF registration transition without uploading files or mutating the registration.
- [x] The monitor emits a redacted receipt and validates a canonical snapshot only for an active public immutable registration.
- [x] One bounded status comment on issue 532 reports the verified state and next release action.
- [x] Papers and preprints remain excluded.

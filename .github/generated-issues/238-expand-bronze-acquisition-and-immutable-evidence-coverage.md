# Expand Bronze acquisition and immutable evidence coverage

Epic: `BRONZE-COVERAGE-001` — Bronze acquisition coverage expansion

Labels: type:data-source, type:provenance, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] Reachable historical payloads are restored through the hardened downloader.
- [x] B1 retains acquired and failed attempts without raw paths.
- [x] B2 contains only deduplicated checksum-bound evidence identities.
- [x] Rights-review state remains distinct from acquisition and fixity.
- [x] Automated and hosted gates pass.

# Expand Bronze acquisition and immutable evidence coverage

Epic: `BRONZE-COVERAGE-001` — Bronze acquisition coverage expansion

Labels: type:data-source, type:provenance, status:in-progress

Status: `in_progress`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [ ] Reachable historical payloads are restored through the hardened downloader.
- [ ] B1 retains acquired and failed attempts without raw paths.
- [ ] B2 contains only deduplicated checksum-bound evidence identities.
- [ ] Rights-review state remains distinct from acquisition and fixity.
- [ ] Automated and hosted gates pass.

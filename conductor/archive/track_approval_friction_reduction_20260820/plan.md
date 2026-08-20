# Implementation plan

- [x] APR-01: Define risk tiers, approval triggers and high-risk exclusions.
- [x] APR-02: Auto-classify deterministic architecture and SBOM outputs as Apache-2.0 project
  outputs.
- [x] APR-03: Add explicit approval requirement, reason code and reapproval trigger fields to the
  publication manifest.
- [x] APR-04: Implement integrity-checked standing dashboard approval with fail-closed material
  change detection.
- [x] APR-05: Add regression tests for automatic project-output classification, standing approval
  reuse and material-change invalidation.
- [x] APR-06: Regenerate governed outputs and run targeted and full repository gates. Local
  validation passed with 558 tests, two optional skips, 90.10% coverage, deterministic byte
  parity, clean type/lint/security checks and successful Python/dashboard builds.
- [x] APR-07: Review, merge through protected CI, synchronize issue #708 and archive this track.
  PR #709 merged at `7e8d239132d6c3b2122b7d7062e6028fac9536c6`; issue #708 is closed.

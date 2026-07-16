# Session: v71 deterministic release manifest

## Implemented

- Added `scripts/make_release_manifest.py` for deterministic tag/commit and subject checksums.
- Added unit coverage for stable ordering, validation and fail-closed path handling.
- Updated the tagged release workflow to build, attest, verify and publish the manifest.
- Updated consumer verification documentation and the public-product Conductor plan.

## Boundary

The manifest and GitHub attestation establish software build provenance only. Zenodo deposition,
OSF registration, Hugging Face publication, source-data licensing and evidence/policy claims remain
blocked until the existing accountable human review and publication gates pass.

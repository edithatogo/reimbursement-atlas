# Session: v72 release-manifest consumer verifier

## Implemented

- Added an offline verifier for release-manifest schema, repository, tag, commit, safe paths and
  SHA-256 subject hashes.
- Added unit coverage for valid subjects, expected metadata and tamper rejection.
- Documented local checksum verification alongside the required GitHub attestation check.
- Promoted the release-attestation roadmap function to implemented.

## Boundary

The verifier proves local artifact integrity and expected release metadata. Only GitHub's
attestation verification proves workflow provenance, and neither mechanism approves source
licensing, OSF, Hugging Face, Zenodo, evidence or policy publication.

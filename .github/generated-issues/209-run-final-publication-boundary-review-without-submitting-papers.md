# Run final publication boundary review without submitting papers

Epic: `RAC-RELEASE-001` — Citation, archive and public record maturity

Labels: type:release, type:review, risk:publication, status:implemented

Status: `implemented`

## Background

This issue was generated from `conductor/backlog.yml`; the criteria below are the track-specific acceptance contract.

## Acceptance criteria

- [x] Zenodo and DataCite payloads, file inventory, checksums, SBOM and attestations validate against the frozen release.
- [x] Mapping, dashboard, licence and release-readiness gates independently pass before deposition.
- [x] The version DOI resolves and remote checksums are verified after publication.
- [x] Papers, manuscripts and preprints are excluded.
- [x] The signed GitHub release precedes Zenodo deposition, and every deposited asset is verified against its exact-tag attestation.

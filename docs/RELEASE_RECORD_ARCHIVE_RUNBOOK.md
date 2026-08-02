# Release Record and Archive Runbook

This runbook defines the fail-closed sequence for a versioned software and
permitted-derived-data release. It does not submit papers or preprints.

## Local preflight

Run from a clean checkout of the exact release commit:

```bash
pixi run citation-validate
pixi run release-readiness
pixi run archive-publication-gate
pixi run public-data-policy
pixi run licence-review-validate
pixi run zenodo-metadata
pixi run zenodo-draft
```

The archive publication gate must report `ready` before a signed release is
created. A missing OSF registration, source-rights decision, mapping review or
release-readiness flag stops the sequence.

## Tagged release sequence

The protected `.github/workflows/release.yml` workflow is authoritative:

1. Validate governance and exact tag identity.
2. Build the wheel and sdist.
3. Generate the source archive and both CycloneDX SBOMs.
4. Freeze `release-manifest.json` with SHA-256, size, tag and commit fields.
5. Generate GitHub artifact attestations for every release subject.
6. Verify each attestation against the release workflow and exact source ref.
7. Publish the GitHub release assets only after verification succeeds.

The release asset inventory must contain exactly these roles: wheel, sdist,
source archive, Python SBOM, dashboard SBOM, release manifest and attestation
receipts. No raw source payloads, secrets, papers or preprints may be included.

## Zenodo and DataCite boundary

After the exact GitHub release assets exist, the token-gated workflow may be
run in order: plan, draft, reserve DOI, verify remote filename/size/SHA-256
parity, and only then publish. OSF must be active and public before any
mutation. The concept DOI is added to `CITATION.cff` in a subsequent commit;
the frozen version release is never rebuilt.

If credentials, OSF state, Zenodo state, rights review or DOI resolution are
unavailable, record the redacted receipt and leave the gate pending. Do not
retry a rejected remote mutation blindly.

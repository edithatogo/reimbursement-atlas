# Release verification

Release artefacts are built by the tagged GitHub Actions release workflow and receive GitHub
artifact attestations. The workflow also publishes `release-manifest.json`, a deterministic
inventory binding the release tag and commit to every distribution, source archive and SBOM.
Verify both the checksum and the attestation before installing a release.

## Requirements

- GitHub CLI with the attestation extension available;
- access to the public repository `edithatogo/reimbursement-atlas`;
- a downloaded release asset and its published SHA-256 checksum, when provided.

## Verify a release asset

Set the tag and local asset path, then verify the artifact against the repository and release
workflow:

```bash
TAG=v0.1.0
ASSET=dist/reimbursement_atlas-0.1.0-py3-none-any.whl

shasum -a 256 "$ASSET"
python scripts/verify_release_manifest.py \
  --manifest release-manifest.json \
  --root . \
  --expected-tag "$TAG"
gh attestation verify "$ASSET" \
  --repo edithatogo/reimbursement-atlas \
  --signer-workflow edithatogo/reimbursement-atlas/.github/workflows/release.yml \
  --source-ref "refs/tags/$TAG" \
  --deny-self-hosted-runners
```

Repeat the attestation command for the source archive and each SBOM selected for use. The release
workflow itself performs the same verification before publishing its GitHub release. Verify the
manifest too:

```bash
gh attestation verify release-manifest.json \
  --repo edithatogo/reimbursement-atlas \
  --signer-workflow edithatogo/reimbursement-atlas/.github/workflows/release.yml \
  --source-ref "refs/tags/$TAG" \
  --deny-self-hosted-runners
```

## Interpret the result

An attestation verifies that the subject was produced by the expected GitHub workflow from the
expected tag. The release manifest additionally lets consumers compare the published subject
checksums. It does not establish that MBS, PBS, CMS, CPT, OSF or Hugging Face publication gates
have passed. Check the release status manifest, source licence records and human-review decisions
before making evidence or policy claims.

The project deliberately separates software release readiness, evidence readiness for reviewed
source bundles, and OSF/Hugging Face/Zenodo publication approval. See
[`apps/dashboard/public/status.json`](../apps/dashboard/public/status.json),
[`docs/RELEASE_READINESS.md`](RELEASE_READINESS.md) and [`docs/LICENSING.md`](LICENSING.md).

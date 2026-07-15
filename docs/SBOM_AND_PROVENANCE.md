# SBOM and provenance strategy

The project now produces release-oriented software bill of materials and provenance hooks before the live-data layer becomes important.

## SBOMs

Generated files:

```text
data/derived/sbom/cyclonedx-python.json
data/derived/sbom/cyclonedx-dashboard.json
data/derived/sbom/sbom_summary.jsonl
data/derived/sbom/sbom_summary.csv
```

The SBOM generator is deliberately simple and deterministic. It reads `uv.lock` for Python packages and `apps/dashboard/package-lock.json` for npm packages. This avoids a fragile optional SBOM dependency while keeping output close to CycloneDX 1.6.

## Provenance

The release workflow now requests:

```yaml
permissions:
  contents: write
  id-token: write
  attestations: write
```

It then attests:

- Python distributions in `dist/*`;
- the source archive;
- generated SBOM JSON files.

## Publication relationship

The publication manifest includes SBOM summaries and SBOM JSON files as derived release-candidate artefacts. It does not include raw source files, local cache paths, restricted terminology dumps or confidential net-price material.

## Consumer verification

Consumers should verify a tagged release before using its software or derived artefacts. The
release workflow attaches GitHub artifact attestations to Python distributions, the source archive
and SBOM files. The repository keeps raw live-source payloads out of those release subjects.

The exact commands and signer checks are documented in
[`docs/RELEASE_VERIFICATION.md`](RELEASE_VERIFICATION.md). Verification is a consumer-side gate;
the presence of an attestation proves build provenance, not licence clearance or evidence
readiness of the underlying research outputs.

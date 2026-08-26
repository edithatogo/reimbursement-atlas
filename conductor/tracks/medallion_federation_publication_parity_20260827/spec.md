# Specification

## Overview

Align the repository's public distribution surfaces with its existing medallion architecture and byte-versioned sibling-repository contracts.

## Requirements

1. Generate a deterministic manifest for medallion contract versions v1-v3, including every schema and conformance fixture checksum.
2. Verify byte-level parity for `reimbursement-atlas`, `global-medicines-atlas`, and `archive-govt-nz` without adding a shared runtime dependency.
3. Record `global-family-justice-data` as adapter-required until its preservation-oriented B0/B1 terminology maps to the shared B0/B1/B2 vocabulary.
4. Generate a federation manifest linking GitHub, Hugging Face dataset/Space, Zenodo, layer roles, checksums, rights boundaries, and publication state.
5. Stage explicit Hugging Face configurations for B0 catalogue, B1 acquisition, B2 evidence, Silver, Gold, Platinum, lineage, and promotion decisions.
6. Replace stale design-stage Hugging Face metadata with current bounded medallion semantics.
7. Keep all remote publication mutations token-gated and separately authorized.

## Acceptance criteria

- Contract hashes are deterministic and validated by tests.
- Live sibling drift is detected by scheduled CI and cannot be mistaken for local conformance.
- The staged Hugging Face tree contains only allow-listed derived/public metadata.
- Dataset metadata distinguishes catalogue, acquisition, evidence, transformation, analysis, and publication states.
- Raw payloads, restricted descriptors, credentials, local paths, and unsupported claims remain prohibited.
- Repository-owned gates and protected hosted checks pass.

## Non-functional constraints

- Python 3.14 and strict BasedPyright remain supported.
- Existing v1-v3 contract directories are immutable.
- Generated outputs must be reproducible and fail closed.
- A sibling repository's incompatible vocabulary is reported, not silently normalized.

## External gates

- Hugging Face publication remains an explicit credentialed workflow dispatch.
- Changes to sibling repositories and `repository-standards` are outside this repository's mutation authority.

## Out of scope

- Publishing papers or preprints.
- Publishing raw or rights-restricted source payloads.
- Declaring `repository-standards` authoritative before it hosts and versions the contracts.

## Authoritative inputs

- `docs/contracts/MEDALLION_ARCHITECTURE_CONTRACT.md`
- `contracts/medallion/v1/medallion-conformance.schema.json`
- `contracts/medallion/v2/field-lineage.schema.json`
- `contracts/medallion/v3/backfill-replay.schema.json`
- GitHub issue #767

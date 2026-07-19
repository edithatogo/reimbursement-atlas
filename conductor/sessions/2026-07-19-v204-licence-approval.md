# v204 Checksum-bound licence approval

Date: 2026-07-19

The repository owner explicitly approved the 11 current checksum-drifted derived
artefacts under the existing grouped licence scope. The approval was recorded by
`scripts/record_licence_approvals.py`, which verified every path and SHA-256 against
the generated queue and rejected raw-source candidates.

The companion decision file now validates at `177/177` rows, all approved. This
approval applies only to the exact derived paths and checksums and does not approve
raw source payloads, restricted descriptors, unsupported evidence or policy claims,
OSF registration, Hugging Face mutation, dataset release or papers.

Remaining gates are source-specific reuse terms, methods/domain/governance review,
mapping adjudication, OSF registration approval, and the final publication gate.

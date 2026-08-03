# Handoff Retention Policy

## Purpose

Handoff bundles and archives are durable recovery artifacts. They are not build
outputs or temporary files and must not be removed during routine repository
cleanup.

## Active handoffs

The active handoff directory retains:

- the current canonical handoff for commit `7a69b328f1cd3736c8379d40081495e43812ca3d`;
- the immediately preceding rollback handoff for commit `81c28d8809c6fe47cf8e3aa2eecc4da1dec244b1`;
- each payload's manifest and SHA-256 sidecar.

The directory is intentionally separate from the Git worktree. The repository
does not track bundle payloads, archive payloads, or local raw-source files.

## Historical archive

Older handoffs are retained in the operator-managed external archive under the
`reimbursement-atlas` archive namespace. They are moved there, not discarded,
so recovery, audit, and historical reproducibility remain possible without
cluttering the workspace.

The external archive must maintain an inventory containing, at minimum, the
relative path, byte size, modification timestamp, SHA-256 digest, artifact
kind, and verification status for every payload. Inventory generation must not
copy raw source payloads into the repository.

## Verification and deletion rules

Before relocation or recovery:

1. verify Git bundles with `git bundle verify`;
2. verify payload checksums with `shasum -a 256` or an equivalent implementation;
3. preserve manifests and checksum sidecars with their payloads;
4. record the operation in the external inventory.

Exact byte-identical duplicates may be removed only after their digest has been
recorded and at least one verified copy remains. Unique historical artifacts,
source provenance, licence decisions, and release evidence must never be
deleted as part of cleanup.

## Scope boundaries

This policy does not authorize publication, OSF/Hugging Face/Zenodo mutation,
paper or preprint submission, or the tracking of raw or licence-restricted
source data. Publication readiness and external registry state remain separate
from handoff retention.

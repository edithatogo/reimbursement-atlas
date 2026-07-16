# Session v89: Apache-2.0 licence metadata normalization

Date: 2026-07-16

## Scope

Resolve the mismatch between the repository's declared Apache-2.0 code licence and GitHub's live
`Other/NOASSERTION` repository metadata.

## Change

- Normalize `LICENSE` to the canonical Apache License, Version 2.0 text.
- Add `NOTICE` for project attribution and the source-data relicensing boundary.
- Extend `scripts/check_public_docs.py` to verify both files.
- Add a unit contract and Conductor backlog item for continued enforcement.

## Boundary

This applies only to project-owned software and documentation. MBS, PBS, CMS, AMA-gated files and
third-party terminology retain their provider-specific terms and remain subject to human review.

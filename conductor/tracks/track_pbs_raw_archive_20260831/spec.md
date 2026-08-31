# Specification

## Scope and authoritative inputs

Implement a bounded offline source-archive utility and cohesive evidence handoff
for issue #255. The owner's current instruction authorizes these repository changes,
including local staging after contract review and tests under the existing owner
authorization. Network publication, external contacts and global regeneration
remain excluded from this worker's execution scope.

- `data/licence_review/pbs_raw_permission.json` and the shared helper at PR #801
  merge `02116d73da8a8f5dee96009b1ec33691d2704062` govern artefact scope.
- `data/derived/historical_sources/pbs_archive_v1/historical_source_downloads.jsonl`,
  `pbs_structured_archive_v1/historical_source_downloads.jsonl` and
  `pbs_archive_verification_v1/internet_archive_variant_receipts.jsonl` under the
  same historical-sources directory bind acquisition, not publication.
- Exact CDX observations in `pbs_archive_verification_v1/internet_archive_cdx_observations.jsonl`
  are required for a replay transport difference; no blind scheme normalization.
- Early-schema metadata originates in commit
  `724e667a4234feea3969a460475feb8a865b1c99`, cherry-picked as `ab321dce`.
- `infra/huggingface/DATASET_CARD.md` retains eight explicit derived configs and
  `license: other`; existing derived-upload raw rejection remains unchanged.

## Acceptance criteria

- A1: Exact size/SHA-256 and safe ignored paths, active permission, original filename,
  complete permission-record checksum, attribution and edition provenance are required.
- A2: Duplicate JSON keys fail closed. Readback verifies payloads, the entire expected
  manifest, checksum-bound README and exact inventory. Operation failures cannot
  claim batch completeness; publication remains `not_asserted`.
- A3: The known HTTP capture binds exact CDX original/timestamp/status/digest to the
  actual payload SHA-1 and receipt SHA-256; all other URL changes fail closed.
- A4: Full-corpus initial and superseding dry-run reports remain retained. Subsets
  never erase missing 1987 or excluded-format-notice coverage.
- A5: Two historical schema distributions remain metadata-only evidence, not four
  recovered monthly releases, schema compilation, API equivalence or a recovered PDF.
- A6: Permission track closes on observed #801 evidence; source track stays active
  pending parent integration/regeneration and protected source-PR delivery.

## Exclusions and external gates

No raw Git payloads, credentials, absolute local paths in tracked evidence, network
publication, publisher/library contacts, scientific claims or new licence grants.
Later transfer to a distinct `raw/pbs/` prefix requires independent review, protected
source-PR green/merge and parent execution with separate publication/readback evidence.
Missing monthly releases and the physical NLA serial lead remain source-recovery work.

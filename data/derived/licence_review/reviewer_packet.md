# Licence review packet

This generated packet is a checklist for an accountable human reviewer. It does not
grant approval, alter the publication manifest, or enable remote publication. Review
the exact candidate file and checksum in `licence_review_queue.csv`, then record one
complete decision row in the human decision record specified by
`docs/REVIEW_DECISIONS.md`. Use the grouped questions in
`docs/LICENCE_DECISION_MATRIX.md` to organise review, but do not replace the
checksum-bound row-level record.

## Current batches

- `permissive_candidate` / `public_derived_candidate`: 135 artefacts, 190294683 bytes
- `permissive_candidate` / `public_metadata_candidate`: 30 artefacts, 231553 bytes
- `public_reuse_review` / `public_derived_candidate`: 17 artefacts, 4144158 bytes
- `public_reuse_review` / `public_metadata_candidate`: 2 artefacts, 938312 bytes

Total candidate artefacts: 184. Neutral generated row markers are not approval
requests; the batch and summary `pending_count` values identify required decisions.

## Decision ledger snapshot

The companion checksum-bound ledger currently records **165 approved**
and **19 blocked** decisions. These counts are informational;
they do not change generated queue rows or authorize publication.

### Blocked rows requiring re-review

- `data/derived/historical_sources/historical_mbs_archive_targets.csv` — `e6b8e47d1c2620e0fe056c6b1c46b48fe33c61051fb8e6cbff43a9d657776faf`
- `data/derived/historical_sources/historical_mbs_archive_targets.jsonl` — `a348e253ba87f94d30786392adba6055f69eb75d87aca2cc2598a1f0798ce9d7`
- `data/derived/historical_sources/historical_mbs_review_queue.csv` — `d5764e13463d937e7f2538d2b2819ac12d3ec80a6b6e79a4aba5d0fae5401744`
- `data/derived/historical_sources/historical_mbs_review_queue.jsonl` — `65ef648f4a10f4e12613ed924350aeec79d724bedd74e547f19da9c64edb5df6`
- `data/derived/historical_sources/historical_source_downloads.csv` — `a3eadc505c7a89d4df018e5234c62d70e3dc3c4cc248a5664c141f65d6646326`
- `data/derived/historical_sources/historical_source_downloads.jsonl` — `8ae141cf09f298669a8421583063a0b0d3ea1bcafb245d1d03288cc7a107df8f`
- `data/derived/historical_sources/historical_source_downloads_summary.json` — `e2958d31e6343e4d7fa939967031d983b8a5e5109a64e52d099c9fd2ef9936db`
- `data/derived/historical_sources/pbs_archive_v1/historical_pbs_archive_targets.csv` — `bdbd4eceb4f50ef3b58a89476807f6c3f6aafaaf4637e41f8f323156ad128e90`
- `data/derived/historical_sources/pbs_archive_v1/historical_pbs_archive_targets.jsonl` — `acba22bc74529fa24cc39e3eaa39671c2822873c526d7c05fca3f25eb07641e0`
- `data/derived/historical_sources/pbs_archive_v1/historical_source_downloads.csv` — `1200728c1f513e8835c6ceaabc76edb1d31dccd099a11c0786b12bf5ca4355e9`
- `data/derived/historical_sources/pbs_archive_v1/historical_source_downloads.jsonl` — `aff99a68d7f7af7e7d2766b80599f75365c06f8c7620f317cf4b15104473772e`
- `data/derived/historical_sources/pbs_archive_v1/historical_source_downloads_summary.json` — `5ff1749d943045f4e7aac911f6355e18382dc6c2e29af141f0f74c470d8349d3`
- `data/derived/historical_sources/pbs_archive_v1/targets_summary.json` — `f93bc4623376c7fd74ceb12d4f8f6df1a86976a646fb37ac25fd81162fc3df45`
- `data/derived/source_downloads/download_plans.csv` — `dfbf82a474da0e6ec3fec9b28a9de97bd31f5806904b9743d7202361462ececf`
- `data/derived/source_downloads/download_plans.jsonl` — `faad224660889d09484f5b2d6bfc2e36901bbb6813f7e19ae1aaaf2407e16e8b`
- `data/derived/source_validation/source_content_validation.csv` — `50c6f39a30cd51f8cc97bcc5f4047074a1f4a2847967589753f7bd53741d53c7`
- `data/derived/source_validation/source_content_validation.jsonl` — `b9371a67d6a7f9fad06b3432f6e87ad7b878d4b126d048a02d35e6d05d99e6ab`
- `data/seed/historical_mbs_archive_targets.jsonl` — `a348e253ba87f94d30786392adba6055f69eb75d87aca2cc2598a1f0798ce9d7`
- `data/seed/historical_pbs_archive_targets.jsonl` — `acba22bc74529fa24cc39e3eaa39671c2822873c526d7c05fca3f25eb07641e0`

## Required decision fields

Each decision must include `review_id`, `relative_path`, `checksum_sha256`, `decision`
(`approved` or `blocked`), `reviewer`, `reviewed_at`, `source_terms`, `attribution`,
`redistribution_permission`, `restrictions`, and `evidence`.

## Review sequence

1. Confirm the candidate checksum still matches the local file.
2. Read the applicable provider terms and record the exact evidence location.
3. Record attribution and redistribution restrictions, including any source-specific terms.
4. Choose `approved` only when redistribution is permitted for this exact candidate;
   otherwise choose `blocked`.
5. Run `pixi run licence-review-validate` and retain the output with the handoff.

The queue is regenerated from the publication manifest. Never edit generated queue rows to
simulate a decision and never treat a passing validator as a substitute for human review.

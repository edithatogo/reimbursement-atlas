# Licence review packet

This generated packet is a checklist for an accountable human reviewer. It does not
grant approval, alter the publication manifest, or enable remote publication. Review
the exact candidate file and checksum in `licence_review_queue.csv`, then record one
complete decision row in the human decision record specified by
`docs/REVIEW_DECISIONS.md`. Use the grouped questions in
`docs/LICENCE_DECISION_MATRIX.md` to organise review, but do not replace the
checksum-bound row-level record.

## Current batches

- `permissive_candidate` / `public_derived_candidate`: 135 artefacts, 190298293 bytes
- `permissive_candidate` / `public_metadata_candidate`: 24 artefacts, 165426 bytes
- `public_reuse_review` / `public_derived_candidate`: 17 artefacts, 4132959 bytes
- `public_reuse_review` / `public_metadata_candidate`: 8 artefacts, 999869 bytes

Total candidate artefacts: 184. Neutral generated row markers are not approval
requests; the batch and summary `pending_count` values identify required decisions.

## Decision ledger snapshot

The companion checksum-bound ledger currently records **159 approved**
and **25 blocked** decisions. These counts are informational;
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
- `data/derived/source_contracts/source_contract_validation.csv` — `93436031f21a626771078353dbfd90390d8f3e3e7281b082da15528542d9f34e`
- `data/derived/source_contracts/source_contract_validation.jsonl` — `576cd9e50605426c0ed50ee5f91535315ed61a2d90adb5284a1fd31249d7f163`
- `data/derived/source_validation/source_content_validation.csv` — `1c8a707de4b06957ec5137dad99193322f72002359454e8dd375738fc5526588`
- `data/derived/source_validation/source_content_validation.jsonl` — `af62160f8c46aafbdcadc0a6f1180d90002a468ffe288ac9a383200b1010778e`
- `data/seed/historical_mbs_archive_targets.jsonl` — `a348e253ba87f94d30786392adba6055f69eb75d87aca2cc2598a1f0798ce9d7`
- `data/seed/historical_pbs_archive_targets.jsonl` — `acba22bc74529fa24cc39e3eaa39671c2822873c526d7c05fca3f25eb07641e0`
- `data/seed/ingestion_readiness.csv` — `bdba5bab3d5ed4673fb48ff4e4fd1010bb2dc6360f8874f0fbd8bfe3fcec893f`
- `data/seed/source_acquisition_plan.csv` — `4d9168740eca26a4b50312b1c634f765f97a194042aef5e9884128d9c5c3a785`
- `data/seed/source_files.csv` — `47cf35fb6436e976fc93af1c8529429a07c65a19920393bcbe0bfa1fe5da6cbd`
- `data/seed/source_files.jsonl` — `a59ae016ac740167baef7740c778d7dbab9e22fd9863843f85f626d01d48bcb2`
- `data/seed/source_versions.csv` — `8e938bce1c3040f4472bfb1f2968fb613b9b45cac3f5d63aacb1c031341dca93`
- `data/seed/source_versions.jsonl` — `eb46d27d17f4b79d315df9a3e8adf24f390bca642c0645de26a4028746440950`

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

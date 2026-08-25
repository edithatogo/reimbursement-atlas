# Licence review packet

This generated packet is a checklist for an accountable human reviewer. It does not
grant approval, alter the publication manifest, or enable remote publication. Review
the exact candidate file and checksum in `licence_review_queue.csv`, then record one
complete decision row in the human decision record specified by
`docs/REVIEW_DECISIONS.md`. Use the grouped questions in
`docs/LICENCE_DECISION_MATRIX.md` to organise review, but do not replace the
checksum-bound row-level record.

## Current batches

- `permissive_candidate` / `public_derived_candidate`: 145 artefacts, 191077097 bytes
- `permissive_candidate` / `public_metadata_candidate`: 35 artefacts, 467075 bytes
- `public_reuse_review` / `public_derived_candidate`: 3 artefacts, 529164 bytes

Total candidate artefacts: 183. Neutral generated row markers are not approval
requests; the batch and summary `pending_count` values identify required decisions.

## Decision ledger snapshot

The companion checksum-bound ledger currently records **180 approved**
and **3 blocked** decisions. These counts are informational;
they do not change generated queue rows or authorize publication.

### Blocked rows requiring re-review

- `data/derived/historical_sources/historical_source_downloads.csv` — `7b029ea5de8cd3225b28e0f6d24d72e9a0266a790439c4c00eb2199217f7dd77`
- `data/derived/historical_sources/historical_source_downloads.jsonl` — `156be14bfc06bd3a4568cbbdde582adadb9fa3ecf390435b44416c0688515348`
- `data/derived/historical_sources/historical_source_downloads_summary.json` — `39441549b326cae50de52340fb8225a7a1673a7cdaa043b4704813d2cb6262d2`

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

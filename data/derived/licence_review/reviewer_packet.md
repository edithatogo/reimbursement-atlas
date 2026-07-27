# Licence review packet

This generated packet is a checklist for an accountable human reviewer. It does not
grant approval, alter the publication manifest, or enable remote publication. Review
the exact candidate file and checksum in `licence_review_queue.csv`, then record one
complete decision row in the human decision record specified by
`docs/REVIEW_DECISIONS.md`. Use the grouped questions in
`docs/LICENCE_DECISION_MATRIX.md` to organise review, but do not replace the
checksum-bound row-level record.

## Current batches

- `permissive_candidate` / `public_derived_candidate`: 174 artefacts, 192494708 bytes
- `permissive_candidate` / `public_metadata_candidate`: 43 artefacts, 625770 bytes
- `public_reuse_review` / `public_derived_candidate`: 2 artefacts, 17987 bytes

Total candidate artefacts: 219; generated queue rows remain `pending` by design.

## Decision ledger snapshot

The companion checksum-bound ledger currently records **217 approved**
and **2 blocked** decisions. These counts are informational;
they do not change generated queue rows or authorize publication.

### Blocked rows requiring re-review

- `data/derived/source_downloads/download_attempts.csv` — `1a29b6ed6d82dd6bba08911ee9abc498d9501e0eff36a144ae20254f618b4144`
- `data/derived/source_downloads/download_attempts.jsonl` — `37b4c857125cd7d4dc2a7e998b8d86ca1306a400fd46a93513a89cce287eb0bc`

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

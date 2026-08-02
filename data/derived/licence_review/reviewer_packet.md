# Licence review packet

This generated packet is a checklist for an accountable human reviewer. It does not
grant approval, alter the publication manifest, or enable remote publication. Review
the exact candidate file and checksum in `licence_review_queue.csv`, then record one
complete decision row in the human decision record specified by
`docs/REVIEW_DECISIONS.md`. Use the grouped questions in
`docs/LICENCE_DECISION_MATRIX.md` to organise review, but do not replace the
checksum-bound row-level record.

## Current batches

- `permissive_candidate` / `public_derived_candidate`: 168 artefacts, 192001112 bytes
- `permissive_candidate` / `public_metadata_candidate`: 43 artefacts, 627747 bytes
- `public_reuse_review` / `public_derived_candidate`: 8 artefacts, 518254 bytes

Total candidate artefacts: 219; generated queue rows remain `pending` by design.

## Decision ledger snapshot

The companion checksum-bound ledger currently records **211 approved**
and **8 blocked** decisions. These counts are informational;
they do not change generated queue rows or authorize publication.

### Blocked rows requiring re-review

- `data/derived/architecture/import_edges.csv` — `691e582bdde7ee8b7130bf389c872a285ac9940d4954ba5066c67cab688170ab`
- `data/derived/architecture/import_edges.jsonl` — `1216a4cf16bb34aa1ce13ef546671da0b721f0cec55beb8c312d6193749937ca`
- `data/derived/sbom/cyclonedx-dashboard.json` — `a502851cdf62459b33153bc03842b845484138661a5b74a9df1e6aec13e90429`
- `data/derived/sbom/cyclonedx-python.json` — `9ebc9578a9062d571db55d1abe5d1038e0256176c1510d24a427f918f74de645`
- `data/derived/sbom/sbom_summary.csv` — `0077ee2c4971840b95f6bd45d08abf2ba879ce443a52d677e83b946af5c2687c`
- `data/derived/sbom/sbom_summary.jsonl` — `de5735c1677b2092ac71a4245e564908bf4bc9d690924e2bf0d51ddb276be612`
- `data/derived/source_downloads/download_attempts.csv` — `132a65d895f0b1f6b2d8b39b522c761fd2a558a913273a39238a72b22d421ada`
- `data/derived/source_downloads/download_attempts.jsonl` — `712ee26c46ddc0107118e0362c820a3b2ed8d27cf0d0be8f9cba525faa4e3d20`

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

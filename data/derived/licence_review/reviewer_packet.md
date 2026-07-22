# Licence review packet

This generated packet is a checklist for an accountable human reviewer. It does not
grant approval, alter the publication manifest, or enable remote publication. Review
the exact candidate file and checksum in `licence_review_queue.csv`, then record one
complete decision row in the human decision record specified by
`docs/REVIEW_DECISIONS.md`. Use the grouped questions in
`docs/LICENCE_DECISION_MATRIX.md` to organise review, but do not replace the
checksum-bound row-level record.

## Current batches

- `public_reuse_review` / `public_derived_candidate`: 135 artefacts, 54085162 bytes
- `public_reuse_review` / `public_metadata_candidate`: 43 artefacts, 597337 bytes

Total candidate artefacts: 178; generated queue rows remain `pending` by design.

## Decision ledger snapshot

The companion checksum-bound ledger currently records **162 approved**
and **16 blocked** decisions. These counts are informational;
they do not change generated queue rows or authorize publication.

### Blocked rows requiring re-review

- `data/derived/data_dictionary/data_dictionary.csv` — `19dbb33ba80931a6d844cc9a4475799fb954b4540b6ff0a5932f14405a80f5b1`
- `data/derived/data_dictionary/data_dictionary.jsonl` — `e2ff6efa149f62249c44174039b3cae674772111c8163d56b3c8113578d849c6`
- `data/derived/data_dictionary/summary.json` — `aeec5919683e84e313151727ef85299a5abe2b0e568f919db5fedfefb0a722e5`
- `data/derived/local_quality_gates/local_quality_gates.csv` — `2e97c8cff9aeadb31d1c935c936e633db97e083eefa220e84a801a8fed8356ee`
- `data/derived/local_quality_gates/local_quality_gates.jsonl` — `9c4181a11353dafaa83e794231d9b31ea06e256a210561fe4b72690ed5bdf5d6`
- `data/derived/release_readiness/release_gates.csv` — `4e1f4e4d5fa60a4dbc274751f1de6ef7afe5e36160b6788c555590d191d4e01c`
- `data/derived/release_readiness/release_gates.jsonl` — `12d4ecc9d39d293fd7254cfdc08b7796485057bf210cdd9e33c920a88fe833bd`
- `data/derived/research_package/datapackage.json` — `0e24788a162aa7c32a7fad56fdc1077ea892dd01513826b37b368bc80f45cf62`
- `data/derived/research_package/dcat.jsonld` — `c89abcde09658d85feb9b1915bfef0a038beca8125bab52cc9cdf8dbd6269799`
- `data/derived/research_package/ro-crate-metadata.json` — `364a9b6e650b34c53b7b4c695e33197cf8b7cfa5b69abf2908e0e97895175bdb`
- `data/derived/sbom/cyclonedx-dashboard.json` — `6539f390e46a2afbffa473ddb394c91c60dd6ee1903d1d593187cb03c5906da4`
- `data/derived/sbom/sbom_summary.csv` — `6b91e15d0942eca4d507c6c53f6653ab70b1b6611dd006ad778c10a922444b2f`
- `data/derived/sbom/sbom_summary.jsonl` — `bb2411b56f895073e84384523a5151ed88f72cee97bc33e796a0961da4bd1119`
- `data/derived/source_downloads/download_attempts.csv` — `bf5e47a37f4bf536e30aeda750cbdab54d84a95a17557b0ab3aae73bb615e02f`
- `data/derived/source_downloads/download_attempts.jsonl` — `2fceba2169fc0e0dc55b03853b7a278f4a98d062a8ff4aa498ceecea4676be27`
- `infra/huggingface/CROISSANT.json` — `ee8c2276069f52613415c89432f88b47503d59f2dbc23840471a7d6e9937de24`

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

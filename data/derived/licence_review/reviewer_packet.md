# Licence review packet

This generated packet is a checklist for an accountable human reviewer. It does not
grant approval, alter the publication manifest, or enable remote publication. Review
the exact candidate file and checksum in `licence_review_queue.csv`, then record one
complete decision row in the human decision record specified by
`docs/REVIEW_DECISIONS.md`. Use the grouped questions in
`docs/LICENCE_DECISION_MATRIX.md` to organise review, but do not replace the
checksum-bound row-level record.

## Current batches

- `permissive_candidate` / `public_derived_candidate`: 162 artefacts, 191581773 bytes
- `permissive_candidate` / `public_metadata_candidate`: 39 artefacts, 523619 bytes
- `public_reuse_review` / `public_derived_candidate`: 14 artefacts, 953126 bytes
- `public_reuse_review` / `public_metadata_candidate`: 4 artefacts, 106459 bytes

Total candidate artefacts: 219; generated queue rows remain `pending` by design.

## Decision ledger snapshot

The companion checksum-bound ledger currently records **201 approved**
and **18 blocked** decisions. These counts are informational;
they do not change generated queue rows or authorize publication.

### Blocked rows requiring re-review

- `data/derived/architecture/import_edges.csv` — `691e582bdde7ee8b7130bf389c872a285ac9940d4954ba5066c67cab688170ab`
- `data/derived/architecture/import_edges.jsonl` — `1216a4cf16bb34aa1ce13ef546671da0b721f0cec55beb8c312d6193749937ca`
- `data/derived/data_quality/data_quality_checks.csv` — `02330e9d0689d7d837736ae2d2eb61fb28fd13cc01b66da971503243a9f784cc`
- `data/derived/data_quality/data_quality_checks.jsonl` — `22cf81321d32c252a00daede3e2895f399013f11099a3d480c275200192936aa`
- `data/derived/github_project/github_project_items.csv` — `8e5a6d433d3b1610e881f103a4d6753f829db457a12b75c69f7c78f9b103162e`
- `data/derived/github_project/github_project_items.jsonl` — `d48e6f0ac94c645ff82169d1971131f97c5db78f050ee99f06f6e094b7291521`
- `data/derived/historical_sources/historical_source_catalog.jsonl` — `a8beb02aeca5c9054732f95e6bb1c4eb509c02186bfb3020cd1233303f8dee02`
- `data/derived/reviewed_source_bundles/bundle_au_mbs_20260701_txt_pair_f3c1caae1fe830ae/source_snapshots.csv` — `0a6be3f65c486a63836ccb2820a6ff30e0ce659c345c8a4aca7d1dde409369d3`
- `data/derived/reviewed_source_bundles/bundle_au_mbs_20260701_txt_pair_f3c1caae1fe830ae/source_snapshots.jsonl` — `5af492ce7e9d8abf458c6f4554ee49ee41e8cb1d93f8cb58985fec0dc7bfb193`
- `data/derived/sbom/cyclonedx-dashboard.json` — `fa8672c0cf141b5f590b57c044d0315df5d84f789254af33d113a4765ffc879c`
- `data/derived/sbom/sbom_summary.csv` — `05c14cfb762fa2f981bb12aaf6f7b2b8b6fb5367536e9507dfcd039489a3fea5`
- `data/derived/sbom/sbom_summary.jsonl` — `c53d48541c7770c451c07d0ff776b95628eaccb14b91db34462dfadeea470e5c`
- `data/derived/source_downloads/download_attempts.csv` — `9b6676e65476ccbb4998a267afe17e430a37a280f8e98a736c71c288c4be1751`
- `data/derived/source_downloads/download_attempts.jsonl` — `7d46470bdcdc885475dcef66875dd787c951f2245b1191d9f303a3968463c928`
- `data/seed/conductor_tracks.csv` — `6bae8df869f33dd60c8e0b24ff6f3aa472bb625718848b809560659f38b3541b`
- `data/seed/conductor_tracks.jsonl` — `1ea3f3b14cb7852a0faa1d0c3fedec9f191a7a28df9b8dfaea8356e104fbf82d`
- `data/seed/graph_edges.csv` — `601e4347b42a58dd1c95d7830fdbd9f8f64b7d5bb3bfafbca1d584360e5baad4`
- `data/seed/graph_nodes.csv` — `eebfc143e01dee0f4e8dd50090c7952cf661972d8887d8eec3f66cff82865297`

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

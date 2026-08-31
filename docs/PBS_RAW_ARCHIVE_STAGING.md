# PBS raw archive staging and source evidence

This is an offline preparation and verification utility, not an uploader. Issue
#255 tracks remaining source coverage and eventual governed raw transfer. The
permission implementation is complete through PR #801 (`02116d73`), separately
from this active [source track](../conductor/tracks/track_pbs_raw_archive_20260831/index.md).

## Immutable source and permission bindings

`scripts/prepare_pbs_raw_archive.py` checks already acquired official schedule PDF
and machine-readable package receipts plus source-identified archive variants.
It requires exact byte size/SHA-256, official source and edition identity, citation,
safe ignored paths without symlinks, and the shared versioned artefact permission
gate. Duplicate JSON keys at any nesting level are rejected before interpretation.
Original source filenames retain case; conflicting receipt filenames fail closed.

Successful manifests bind the complete permission record's exact bytes by SHA-256.
Permission is an owner attestation, not an independently verified publisher grant.
PBS source bytes retain original notices, attribution and disclaimers and are not
relicensed as software Apache-2.0. Credentials, diagnostics and absolute local
paths are not projected into archive metadata.

The new staging manifest schema is `pbs-raw-archive-staging-v2`. It distinguishes
failed acquisition-receipt checks from failed staging/readback operations. Either
failure makes `complete_for_requested_batch` false; neither implies historical
completeness. `publication_state` is always `not_asserted`.

## Exact archive identity, not scheme normalization

The May 2011 variant receipt identifies a 5,249,813-byte payload, SHA-256
`63700cc67aa607dbeebce5225ca2f65706e8481ad79cb01b85a146ef3dcc2518`.
The actual cached bytes also have CDX SHA-1 base32
`HN5UW3KS4BUZNGASA5HS4AHFT5UTZ5KH`. The retained CDX observation names
`http://www.pbs.gov.au/publication/schedule/2011/05/2011-05-01-general-schedule.pdf`
at timestamp `20120227130402`, status 200, MIME `application/pdf`.
Its canonical metadata SHA-256 is
`4ff6ded90ccb063bba2c5f49c8fc3b30397a23e9d2e7ac3b5f255e2de1d316c1`.

The official parent receipt names the HTTPS form of that exact host/path. The
utility accepts this transport-only difference only with a unique exact CDX
original/timestamp match, both receipt SHA-1 fields matching the observation,
actual payload SHA-1 matching CDX, and receipt size/SHA-256 matching actual bytes.
Other hosts, paths, queries, capture timestamps, digests or conflicting observations
fail closed. The original HTTP capture and HTTPS official URL remain distinct
manifest fields. CDX `length` is archive-record metadata, not payload byte size.
No fresh CDX network query was made by the staging worker.

## Actual-cache dry-run observations

The initial complete report is retained at
`data/local/pbs-raw-archive-full-dry-run-20260831T033612Z.json`:
1,706/1,709 receipts verified, 9,211,521,622 bytes; three explicit failures.
Its SHA-256 is `91b90bfa4b94acb8d464e7816c9cb1543e1e511571b264bcba44d3b382f198fb`.

The superseding complete report is retained at
`data/local/pbs-raw-archive-full-dry-run-20260831T044559Z.json`:
1,707/1,709 receipts verified, 9,216,771,435 bytes. Verified categories are 1,047
official PDFs, 655 structured packages and five archive variants. The two remaining
failures are December 1987 RPBS `not_acquired` and the format notice
`updated-pbs-text-files.pdf` outside schedule-artefact permission scope.
Full-batch exit status remains 1 and nothing was staged or uploaded. The helper,
permission record, receipts and CDX file had unchanged hashes across the rerun.
Local report files remain ignored; tracked evidence contains only their metadata.
The superseding report SHA-256 is
`708eee4d600b8c5003736f4b15342c4130889b7d9e231bc1a26bc685daec7432`.

## Bounded operation

Run from the integrated repository root with its Python 3.14 environment:

```sh
# Preserve the entire stdout JSON in ignored evidence storage, outside any stage.
PYTHONPATH=src:. python scripts/prepare_pbs_raw_archive.py

# After independent review: orchestrator uses the existing owner authorization.
# Include official parent receipts for every selected archived variant.
PYTHONPATH=src:. python scripts/prepare_pbs_raw_archive.py \
  --receipts data/local/pbs-eligible-receipts.jsonl \
  --stage data/local/pbs-stage

# Separately obtained local copy of that same bounded stage; no network in this command.
PYTHONPATH=src:. python scripts/prepare_pbs_raw_archive.py \
  --receipts data/local/pbs-eligible-receipts.jsonl \
  --readback data/local/pbs-readback
```

The eligible-subset file is now prepared at
`data/local/pbs-raw-archive-selected-20260831T044559Z.jsonl`; it retains unchanged
original receipt lines for all 1,707 eligible rows, including parents and variants.
Its SHA-256 is `66ea4886c44096642dddfaaf80662696237f88170ed814e7155f082aad6a8f19`.
The permission snapshot SHA-256 is
`ad60a2faa3ba5e2544f85e1a4ddb012f3caf2657719c817029aa3af26e5d6d3a`.
No real stage has yet been created; local staging is authorized after contract
review and tests, without another owner approval.
Never edit the original receipt collections to erase omissions. Retain the initial
and superseding full dry-run errors/coverage separately from an eligible subset and
bind them in any later publication receipt. Selection is explicit, not automatic.

A new stage contains only `raw/pbs/payloads/`, `raw/pbs/manifest.json`, and a
checksum-bound `raw/pbs/README.md`. Readback reconstructs the expected stage from
the same trusted acquisition receipts and current permission record, checks every
payload and all manifest provenance, and requires exact README bytes/file inventory.
Missing or altered manifests, permission bindings, extra files/directories and
symlinks fail closed. JSON whitespace/key ordering may differ without changing
manifest meaning; ambiguous duplicate keys may not. Older v1 manifests are not
accepted as equivalent to the new v2 contract. Original raw caches need not remain
present during readback. The tool assumes a non-hostile single-writer filesystem.

## Early schemas and delivery boundaries

[Early-schema evidence](PBS_EARLY_SCHEMA_RECOVERY.md) records two schema distributions
and three digest-verified HTML indexes, not December 2006-March 2007 monthly releases.
Illustrative XML is not release evidence; schema compilation, monthly schema
assignment and API equivalence remain unverified. The NLA serial holding is a lead,
not an inspected or acquired December 1987 PDF. These schema packages are not inputs
to the schedule-only staging utility and receive no automatic artefact approval.

The [dataset card](../infra/huggingface/DATASET_CARD.md) adds conditional `raw/pbs/`
documentation while retaining all eight explicit derived configs and `license: other`.
Existing derived allowlists and raw rejection are unchanged. Any later raw transfer
uses a distinct reviewed path after independent review and protected source-PR
green/merge, preserving existing dataset configs/card. A separate parent publication
receipt must bind the merged implementation, transfer and independent readback.
Isolated full regeneration completed after merging #799, with all 27 native
CI-profile quality gates passing and pytest bounded to four workers. PR #800 merged
as `5bb88f2b`; action inventory and downstream projections were refreshed before
source-PR push. The final four-worker suite passed 916 tests with 90.29% coverage.
Protected source checks and delivery remain separate from
local validation. Publisher/library contacts, raw upload and new owner approval
are not part of this worker's implementation evidence.

The derived dataset workflow clones with `GIT_LFS_SKIP_SMUDGE=1`, so a future raw
archive remains as Git LFS pointers during derived-only publication rather than
downloading its payloads. The guard applies only to the dataset clone, not the
Space clone. It adds no deletion or raw-allowlist exception and preserves the
existing raw pointer tree.

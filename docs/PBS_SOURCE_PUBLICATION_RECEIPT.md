# PBS source publication receipt

This is bounded publication evidence, not an uploader or a new owner-approval gate.
The source implementation track is archived in this closeout change. Its historical
[pending receipt](../conductor/archive/track_pbs_raw_archive_20260831/publication-receipt.pending.json)
is not a publication-completion receipt and must not replace the existing derived
HF publication receipt, staging manifest, or original failed inventory receipt.

## Current evidence

PR #803 merged as `e5c3190efd044fe3bd6b677bb9cf576210d5f9bf`. The retained proofs bind
raw upload revision `8e062578f14e12cf3238700a93946339da9c5d88`: 1,707 payloads,
9,216,771,435 payload bytes, plus manifest and README (1,709 archive artefacts).
The inspected inventory has no missing or mismatched raw entries. Its original
overall strict failure is retained unchanged, not relabelled a global pass.

The inspected bounded metadata reconciliation records exactly 963 additive
per-file `.gitattributes` rules for expected raw LFS PDFs, preserving original
attribute bytes and nonraw effective attributes. All 1,615 LFS payloads are
correctly attributed and all 92 regular Git payloads remain non-LFS. Exactly
23/24 nonraw files are byte-identical; `.gitattributes` is the explicit technical
exception. The eight explicit config files and root card remain unchanged.
No blanket raw LFS rule or synthetic service-derived tags are authorized here.

Earlier viewer observations returned HTTP 500 `ResponseNotReady`. Final bounded
observation 03, completed `2026-08-31T11:51:58.610635+00:00`, supersedes that pending
state: all eight first-rows requests returned HTTP 200, all five viewer validity
flags were true, and eight parquet files were listed with no pending/failed configs.
The receipt binds that actual observation and timestamp. It remains a dated,
non-revision-pinned service observation, not a raw-byte proof or causal upload claim.
Viewer availability is not a prerequisite for asserting verified raw bytes.

The parent completed independent fresh fixed-revision download and canonical
readback. Their native proofs are `data/local/pbs-hf-independent-download-20260831.json`
(SHA-256 `38727f7ab590384f77bada045aeab2a06c412230e2aadd27edc9b40d8d300524`)
and `data/local/pbs-hf-independent-readback-20260831.json`
(SHA-256 `b0b259acc58b02b46203f734cbfb7b605362b51f87b5eb469617963f0ee851d6`).
The historical draft retains an empty fresh-readback slot; the final portable
receipt binds the successful independent readback. The earlier local-stage
readback is not a substitute. PR #804 merged as `a566c425dbf025ac58219912cde72c58a1e8ea0c` and
#802 as `f9703e7904844a21e0e734f697690d0e9464d0f0`. Final integration validation
is distinct from publication verification. Independent P1/P2 semantic review passed.

## Contract and minimal check

`PublicationReceipt` in `src/reimburse_atlas/pbs_publication_receipt.py` defines the
machine-readable contract; `PublicationReceipt.model_json_schema()` exposes its
structural JSON Schema. Runtime validation additionally enforces cross-field
revision, manifest, count, preservation and omission invariants. Unknown fields,
boolean/numeric coercions and duplicate JSON keys fail closed.

From the isolated worktree, using an existing Python 3.14 environment:

```sh
PYTHONPATH=src:. python scripts/check_pbs_publication_receipt.py \
  data/derived/publication/pbs_source_publication_receipt.json \
  --evidence-root .
```

The default checks publication evidence and returns exit 0 with
`status: publication_verified` when those proofs pass. It separately reports
`final_integration_validation_missing` while `closeout_delivery` is null.
Add `--require-integration` to require an exact-commit software validation envelope;
that mode returns exit 1 until the separate envelope exists. Normal protected CI
remains mandatory for merging this implementation. A dirty-worktree QA run must
not be represented as validation of its base commit. The historical preparation
fixture still returns exit 1 with `publication_state: not_asserted`.
The checker hashes and parses the
same bound JSON bytes, then validates native proof semantics. Arbitrary non-JSON
attestations, duplicate keys, mismatched schemas, contradictory results and reuse
of the failed inventory as download/readback/validation proof fail closed.
On failure the effective publication state is `not_asserted`; the input's state
is reported separately as `claimed_publication_state`.

Download proof must be `pbs-fresh-download-v1`, with successful forced non-XET
download, exact metadata inventory/count/revision, and matching manifest/counts/bytes.
Readback must be native v2, verified/readback mode, zero failures and empty errors,
matching counts/byte sum, unique IDs/paths and exact README/permission hashes.
Its exact ID set and each file's SHA-256/byte size, source/version/citation,
original filename, acquisition status and deterministic archive path must match
the selected canonical receipts. Archive variants also bind their selected parent,
timestamp and replay URL. Every complete readback row must equal its row in the
superseding full-corpus report, preserving CDX identity fields and rejecting
unbound extra provenance. Rehashing a fabricated readback does not substitute for
these canonical comparisons. Another legitimate canonical selection cannot substitute. The
checker reconstructs stage-mode serialization to verify the staged manifest hash.
Source delivery must contain the native merged PR SHA and successful check results.
The strict metadata failure is accepted only as raw-inventory evidence alongside
the actual bounded reconciliation's checks and preserved failure hash.

An optional `pbs-closeout-validation-v1` JSON envelope must contain `status: pass`,
the exact `validated_commit`, `pr802_merge`, `pr804_merge`,
`regeneration_fixed_point_verified: true`, and the native CI `local_quality` summary:
positive gate count equal to passed count, no failed/blocked/missing/timed-out/
wrong-tool/skipped gates or blocking failures. Hashes and hand-set outer booleans
cannot substitute for these native evidence contents. If supplied, invalid
integration evidence fails even in default publication-validation mode.

This is offline evidence validation, not a fresh remote attestation or payload
verification run. It never downloads, uploads, promotes, regenerates or archives.
Evidence files must remain available; missing, altered or symlinked evidence fails.

## Parent completion procedure

Keep the tracked `.pending.json` as a non-promoted preparation fixture. Fill a
separate local receipt, then retain the reviewed final metadata at
`data/derived/publication/pbs_source_publication_receipt.json` during final integration.
The final `published_verified` contract rejects every `data/local` evidence reference.
Copy licence-safe native metadata unchanged into
`data/derived/publication/pbs_source_evidence/`, retaining original SHA-256 bindings,
and point the final receipt there. Keep the actual failed inventory JSON and all
superseding proofs; do not substitute a summary or rewrite a failed receipt as pass.
Do not copy raw payloads, credentials, operational logs, or absolute local paths.

The portable receipt and nine unchanged metadata snapshots are present
at those derived paths. Newton's independent P1/P2 semantic re-review passed
(81 receipt tests); the actual raw-publication proofs support `published_verified`.
`closeout_delivery` remains null rather than mislabelling pre-commit local QA.
Protected delivery is independently recorded by the PR and final handoff. The branch includes
`main` at `f9703e7904844a21e0e734f697690d0e9464d0f0`. Neither this preparation nor
the forthcoming source implementation closeout closes source-recovery issue #255
or the TypeScript 7 compatibility watch in issue #362.

1. Retain the fresh-download provenance report and successful canonical-bound CLI
   readback report. Record their paths/hashes in `fresh_readback`, with the exact
   upload revision and staged manifest hash, payload count/bytes and all four
   verification booleans true. The download must be independent and revision-pinned;
   an inventory-only or local-cache run does not qualify. Preserve the original
   staged manifest bytes and their `not_asserted` publication field.
2. Review all referenced evidence and set the separate receipt's publication state
   to `published_verified` only after all raw-publication blockers clear. The
   validator never sets that value automatically, even with complete evidence.
3. After #804 and #802 merge and final facts settle, integrate this implementation,
   regenerate affected projections once, run the required quality/hosted checks,
   and record exact-head delivery in the PR and final handoff. An optional
   `closeout_delivery` must bind a real validated commit and retained validation
   report. Do not infer exact-head validation from older QA.
4. Only then reconcile Conductor seed/CSV, backlog, issue/Project, package/dashboard
   projections and archive the implementation track through reviewed delivery.
   Keep issue #255 source-recovery gaps and the viewer observation distinct.

No additional owner approval is requested for this already authorized scope.
Never track raw payloads, credentials, absolute local paths, or fabricated proof.
Keep both full-corpus dry runs, the excluded format notice, missing December 1987
RPBS bytes, unrecovered early monthly releases, and the uninspected NLA lead.

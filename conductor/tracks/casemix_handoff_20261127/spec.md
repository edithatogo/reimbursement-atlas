# Casemix metadata handoff

Tracking issue: [#880](https://github.com/edithatogo/reimbursement-atlas/issues/880).

## Purpose

Receive a version-qualified Casemix evidence manifest using existing B0/B1/B2 and
Silver/Gold/Platinum contracts, while keeping metadata admission separate from
rights review, scientific review and publication.

## Requirements

- Reuse the existing medallion Pydantic models and preserve their layer semantics.
- Bind source/version, provider URL, payload checksum, size and rights across B0/B1/B2.
- Admit only immutable hash references, never retained source bytes or source content.
- Constrain free-text fields to fixed intake statements and reject duplicate JSON keys.
- Bind artifact input IDs to checksums and preceding layers, including candidate decisions.
- Reject approved promotions and self-attested human decisions in this untrusted envelope.
- Leave the existing licence ledger, standing scope and publication allowlist unchanged.

## Acceptance criteria

1. A valid blocked candidate handoff emits a metadata-only admission receipt.
2. Source/hash/size/rights mismatches, missing predecessors, layer skips, private paths,
   raw payloads and descriptor-bearing free text fail validation.
3. Claimed gate passes cannot replace a checksum-bound accountable decision.
4. Focused tests, lint and type checking pass; required repository/hosted gates remain
   independently recorded before merge.

## External boundary

The 19-path standing metadata scope does not authorize these new source products.
Any future source-derived publication must use the existing accountable review and
checksum-bound human licence ledger. This implementation neither creates nor imports
a human decision and does not change source registries or public products.

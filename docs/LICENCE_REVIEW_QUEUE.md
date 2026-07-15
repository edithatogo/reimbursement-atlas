# Licence review queue

The generated queue at `data/derived/licence_review/` is the artifact-level preparation surface
for human licence and redistribution review. It binds every candidate publication artefact to its
current SHA-256 checksum, publication scope and source-specific licence gate.

The queue is intentionally fail-closed:

- every regenerated row starts with `review_status: pending`;
- generation cannot set `approved`, `publish_allowed`, or any equivalent decision;
- approval requires a named human reviewer, review date, source terms, attribution,
  redistribution decision, restrictions and evidence in `docs/REVIEW_DECISIONS.md`;
- raw source payloads and licence-gated descriptors remain excluded from public bundles.

Run `pixi run licence-review-queue` after changing the publication manifest. Review the generated
CSV/JSONL against the exact checksums, then record decisions in the human review table. A green
software gate or a generated queue is not licence approval.

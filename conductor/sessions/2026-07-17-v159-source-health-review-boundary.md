# Session v159: source-health review boundary

## Scope

Reconcile the source-acquisition monitor with the actual network-enabled evidence without
weakening licence or publication gates.

## Implementation

- Count redacted acquisition outcomes from `download_attempts.jsonl`.
- Report `review_required` when all remaining rows are `skipped_licence_gate`.
- Expose operational-blocker and licence-review counts in JSON, Markdown and CSV evidence.
- Keep operational failures (`incomplete`/`unknown`) fail-open in the GitHub issue workflow.
- Close the duplicate acquisition issue for review-only status while retaining publication blocks.
- Add focused tests for the review-only classification and secret-value redaction boundary.
- Exclude licence-review governance outputs from research-package resources to prevent a
  descriptor/queue checksum cycle.

## Evidence

The current report has three downloaded executable targets, six licence-gated skips, zero
operational blockers and zero credential/network blockers. Human licence review remains required
before derived source promotion or public evidence release.

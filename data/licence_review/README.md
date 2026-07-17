# Human licence decisions

The optional `decisions.jsonl` file is the machine-readable companion to
`docs/REVIEW_DECISIONS.md`. Add one JSON object per human decision only after
reviewing the exact checksum-bound queue row. The validator requires a named
reviewer, review date, source terms, attribution, redistribution permission,
restrictions and evidence. Never add secrets or raw source payloads here.

Use [`decision.schema.json`](decision.schema.json) to validate each JSONL object
before running the repository validator. The schema describes the shape of a
decision; it does not approve any candidate or change publication state.

Run `pixi run licence-review-validate` after editing this file. An empty or
missing decisions file is valid and means that all queue rows remain pending.

# Human mapping decisions

The optional `decisions.jsonl` file is the machine-readable companion to the
mapping review queue and `docs/REVIEW_DECISIONS.md`. Add one object only after
reviewing the exact candidate row and its source evidence. The decision must be
made by an appropriately qualified reviewer; automated similarity is not
adjudication.

Use [`decision.schema.json`](decision.schema.json) to validate each object, or
run `pixi run review-schemas` to validate both review contracts locally and in
CI.
The schema records the candidate identity, confidence, human outcome, reviewer
role, relationship, scope and unit checks, evidence and rationale. It does not
approve the generated queue or change evidence-readiness state by itself.

Do not add source payloads, secrets, or unreviewed approvals. An empty or
missing `decisions.jsonl` remains valid and means all mapping candidates stay
pending. Mapping decisions must not be used as billing, clinical, legal or
policy equivalence without the separate evidence and research gates.

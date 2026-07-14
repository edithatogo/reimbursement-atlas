# Research Protocol Review Checklist

Use this checklist for each protocol before OSF preregistration, public claims, or
publication of policy-facing derived outputs. A completed checklist is evidence
of review coverage, not a substitute for accountable human approval.

## Review Record

| Field | Value |
| --- | --- |
| Protocol ID | `rq_...` |
| Protocol path | `protocols/...` |
| Review version | `YYYY-MM-DD` |
| Reviewer(s) | Named human reviewer(s) |
| Decision | `revise`, `approved for preregistration`, or `blocked` |
| Decision rationale | Link to review notes or issue |

## Required Checks

- [ ] Research question, estimand, outcomes, inclusion rules, exclusion rules,
  and analysis window are explicit.
- [ ] Required datasets and exact source-file records are present in the
  Conductor registry and linked to a source version.
- [ ] Retrieval URLs, redirect evidence, checksums, byte counts, and retrieval
  dates are recorded for each reviewed source.
- [ ] Licence, attribution, redistribution, privacy, and data-governance terms
  have been checked for every source and derived output.
- [ ] Parser, source-content, source-contract, data-quality, and drift checks
  have passing or explicitly explained results.
- [ ] Mapping rules, terminology versions, adjudication requirements, and
  negative controls are defined before interpreting results.
- [ ] Missing-data, denominator, uncertainty, multiplicity, and sensitivity
  rules are frozen and tested.
- [ ] Human clinical, policy, methods, and licence review responsibilities are
  assigned; simulated review is not treated as approval.
- [ ] Proposed OSF components, reports, data dictionary, and publication
  manifest are complete and consistent with the protocol.
- [ ] The final decision and unresolved blockers are recorded in Conductor,
  generated handoff outputs, and the linked GitHub issue.

## Decision Rules

- `revise`: the protocol has material gaps that can be fixed locally.
- `approved for preregistration`: all checks are complete and an accountable
  human reviewer has approved the preregistration package.
- `blocked`: an external licence, access, ethics, clinical, methods, or human
  judgement gate remains unresolved.

No protocol may be labelled `evidence_ready`, published, or preregistered from
this checklist alone. The release-readiness and evidence-readiness generators
remain authoritative for repository status.

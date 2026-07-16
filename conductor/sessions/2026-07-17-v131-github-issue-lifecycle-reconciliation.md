# v131 GitHub issue lifecycle reconciliation

## Scope

Synchronize remote GitHub issue bodies and Project 18 state with the generated Conductor issue
contract after the status-aware renderer was merged.

## Results

The following implementation-complete issues were synchronized from their tracked generated drafts,
commented with the closure rule, and closed: `#326`, `#330`, `#339`, `#340`, `#341`, `#342`, `#343`,
`#344`, `#345`, `#346`, `#351`, `#353` and `#354`. Project 18 read-back reports each row as `Done`.

The generated drafts contain four checked local implementation criteria and explicitly state that
implementation status does not grant external licence, evidence, research or publication approval.
Remaining open issues are release plans, source acquisition/review, OSF/Hugging Face/Zenodo gates,
TypeScript 7 compatibility and account-level security controls.

## Decision

Use the generated source status plus the absence of unchecked implementation criteria as the
automatic closure rule. Preserve external approval boundaries in issue bodies and do not infer
publication readiness from a closed implementation issue.

# Session v43: OSF plan Pixi fix

## Scope

Repair the token-gated, non-mutating OSF workflow after safe discovery passed but the
OSF plan job failed before its CLI contract check.

## Findings

- OSF discovery run `29443897858` passed with the repository secret and did not mutate OSF.
- Go 1.26.5 and `github.com/edithatogo/osf-cli-go` `v1.0.0` installed and verified.
- The OSF plan job failed because `pixi` was not present on the runner (`exit code 127`).

## Change

Add the repository-standard SHA-pinned official Prefix.dev Pixi action to the OSF plan
job before `pixi run osf-cli-contract`. Keep publication and provisioning unchanged and
fail closed.

## Follow-up

Dispatch discovery again after merge. Confirm the plan job passes and inspect only the
sanitized discovery artifact. Publication, registration and human methods/licence review
remain blocked until their existing gates are explicitly satisfied.

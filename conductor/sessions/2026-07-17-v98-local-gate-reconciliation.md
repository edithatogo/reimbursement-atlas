# Session v98: local gate and backlog reconciliation

## Scope

Re-audited merged `main` after commits `55e8771` and `e77decd`, then reconciled
Conductor rows against executable repository evidence and live branch-protection
read-back.

## Implemented evidence

- RxNav-in-a-Box-compatible local adapter configuration, deterministic request
  construction and minimal derived-match parsing are implemented and unit-tested.
- Protocol scaffolds contain source-specific estimands, missingness, mapping,
  uncertainty, sensitivity and amendment sections; the shared reviewer checklist
  is applied before preregistration.
- OSF publication actions are gated by protocol status and the pinned CLI surface
  has an unauthenticated contract test.
- Protected CI includes strict pip-audit, full-history Gitleaks and reproducible
  Python-build checks.
- GitHub branch protection live read-back requires the security and harness
  contexts with strict status checks.

## Explicit blocker

GitHub account-level non-provider secret-pattern scanning and secret-validity
checks remain unavailable. The backlog now records that item as `blocked`; no
secret value or token is recorded in repository artefacts.

The machine's `/opt/homebrew/bin/osf` was an unrelated older `0.3.2` binary and
failed the project contract. Installing the official `github.com/edithatogo/osf-cli-go/cmd/osf@v1.0.0`
into ignored `/tmp/osf-v1-current` with Go 1.26.5 passed the unauthenticated
contract. The repository gate therefore remains pinned to `1.0.0`; callers must
select the official binary rather than trusting an ambiguous PATH entry.

## Boundary

These reconciliations prove software, workflow and metadata implementation only.
They do not approve source licences, research protocols, mappings, OSF
registration, Hugging Face publication or evidence/policy claims.

# Session v138: output issue body reconciliation

Date: 2026-07-17

## Scope

Synchronize remote GitHub output-plan issue bodies with the versioned generated issue
drafts without changing their status or external release gates.

## Evidence

The following issues were updated from `.github/generated-issues/`:

- #114, #115, #116, #117, #118 and #121
- #347, #348, #349 and #350

The generated drafts contain checked repository-owned scope, governance and validation
criteria plus an unchecked promotion/review criterion for planned or drafted outputs.
Remote issue bodies now match those drafts, subject only to GitHub's normalized final
newline. No issue was closed, approved, published or otherwise promoted.

## Outcome

Generated issue content and remote issue content are reconciled. OSF, Hugging Face,
Zenodo and research publication gates remain independently open where applicable.

# Session: approved scope reconciliation

## Scope

The approved repository-owned work is represented by the Conductor tracks and backlog
items for source acquisition and provenance, mapping/evidence review, dashboard review,
OSF metadata, Hugging Face publication, Zenodo draft creation, and final handoff. Papers
and preprints remain explicitly excluded.

## Current evidence

- PRs #634, #635, #636 and #637 merged into `main` after the required hosted checks passed.
- Hugging Face workflow run `30422589083` passed candidate validation but both remote
  pushes were rejected with invalid credentials. No remote mutation was verified.
- Zenodo remains a token-gated draft action. The configured token previously failed before
  mutation because it contained a non-ASCII en-dash; no draft or DOI was created.
- Historical source inventory and acquisition automation remain metadata/derived-only;
  unreviewed raw payloads remain excluded from tracked files.
- PR #640 merged as `b8b02b618a86812352ae4a6758b25a144eb443f5`, after the complete
  hosted matrix passed. Dashboard packets were refreshed for that commit; the
  accountable review record remains pending because the owner approval is bound to
  the prior packet hashes.

## Boundary

Repository candidate readiness is not external publication. The redacted
`huggingface_remote_receipt.json` records the latest failed mutation attempt, and the
final handoff now reports the Hugging Face credential blocker separately from local
candidate readiness. A Zenodo draft is tracked separately from publication or DOI minting.

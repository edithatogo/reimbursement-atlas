# Session v85: MBS derived bundle revalidation

Date: 2026-07-16

## Scope

Reprocess the locally cached July 2026 MBS IMAP/descriptor TXT pair through the reviewed-source
bundle workflow and refresh the derived provenance outputs without tracking raw source payloads.

## Evidence

- `reviewed-mbs-txt-pair-bundle` completed for `au_mbs_20260701_txt_pair`.
- `scripts/check_public_data_policy.py` passed.
- Source-content validation wrote 9 rows.
- Source-contract validation wrote 9 rows.
- Data-quality wrote 41 checks.
- Evidence-readiness wrote 5 rows.
- Licence-review validation passed with 0 human decisions; all candidate artefacts remain pending.
- Release readiness remains 36/36 repository gates passing, while research/publication flags remain false.

## Boundary

The raw MBS files remain in ignored `data/raw_live/` and are not committed. The tracked bundle
contains derived outputs and redacted provenance only. `public_reuse_review` is unchanged because
MBS Online terms require licence review for redistribution. Current PBS acquisition is still
blocked because `PBS_API_SUBSCRIPTION_KEY` is not available in the repository environment.

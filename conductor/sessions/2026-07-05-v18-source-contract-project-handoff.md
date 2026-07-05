# Session: v18 source contract, GitHub Project and final handoff layer

## Implemented

- Added source-specific source-contract validation for MBS TXT, PBS CSV-style extracts and gated CMS targets.
- Added GitHub Project import rows generated from Conductor tracks and generated issue drafts.
- Added final handoff tasks with command, environment and unblock condition for network/credential/review-dependent work.
- Added dashboard-safe CSV outputs for source contracts, GitHub Project items and final handoff tasks.
- Added docs and ADR 0031.

## Why

The repo is ready to move into a network-enabled environment. The remaining tasks should be operationally explicit rather than narrative TODOs.

## Next local commands

```bash
PYTHONPATH=src reimbursement-atlas source-download-plan --method curl
bash data/derived/source_downloads/download_commands.sh
PYTHONPATH=src reimbursement-atlas source-validation
PYTHONPATH=src reimbursement-atlas source-contracts
PYTHONPATH=src reimbursement-atlas reviewed-mbs-txt-pair-bundle \
  data/raw_live/au_mbs/20260701_MBSONLINE_IMAP.TXT \
  data/raw_live/au_mbs/20260701_MBSONLINE_DESC.TXT
```

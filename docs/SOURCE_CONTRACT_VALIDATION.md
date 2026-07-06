# Source contract validation

`source-validation` checks whether a local source file exists and whether it is broadly safe to inspect. `source-contracts` is stricter: it checks source-specific markers, expected columns and parser-facing assumptions before a reviewed-source bundle is allowed to parse the file.

The contract layer is intentionally metadata-only. It records column names, marker presence, byte size, status and recommended action; it never copies raw source payloads or local filesystem paths into public outputs.

## Commands

```bash
PYTHONPATH=src reimbursement-atlas source-validation
PYTHONPATH=src reimbursement-atlas source-contracts
```

Generated artefacts:

```text
data/derived/source_contracts/source_contract_validation.jsonl
data/derived/source_contracts/source_contract_validation.csv
data/derived/source_contracts/summary.json
apps/dashboard/public/data/source_contract_validation.csv
```

## Current contracts

- MBS July 2026 item-map TXT: expects the live headers `ITEM`, `MAPPED_ITEM`, `Item_Start_Date`, `Item_End_Date`, `Item_reuse_flag`, `Mapped_Item_Desc`, `Mapped_Item_Category`, `Mapped_Item_Group`, `Mapped_Item_Subgroup`, `Mapped_Item_Subheading`, `CATEGORY_DESC`, `GROUP_DESC`, `SUBGROUP_DESC`, `SUBHEADING_DESC`, `BTOS`, `BTOS_DESC`, `MODIFY_BBI_FLAG`.
- MBS July 2026 descriptor TXT: expects the live headers `ITEM`, `DESCRIPTION_START`, `DESCRIPTION_END`, `LATEST`, `Description`.
- CMS CLFS landing-page record: skipped until the extracted local ZIP is reviewed.
- PBS API/CSV reviewed extract: expects a PBS item code, medicine label and effective date field once a reviewed CSV extract is staged.
- CMS CLFS / ASP / PFS rows remain gated when they require manual licence review, landing-page extraction or CPT descriptor safeguards.

## Release posture

A missing local raw file is a warning in the current sandbox because source hosts are network-blocked or intentionally not downloaded. A failed contract is blocking: it means the downloaded file looks different from the parser assumption and must be reviewed before parsing.

When release-readiness reports `source_contract_validation_summary` as a warning, treat
that as a real regression. In the current implementation the MBS reviewed bundle and
landing-page skips are aligned so the summary should pass once the source contracts are
rerun after live acquisition.

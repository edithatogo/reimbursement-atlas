# Session v154: Governed PBS acquisition refresh

## Objective

Run the repository-owned source-health workflow with the configured PBS secret and record the
strongest current redacted evidence without committing raw payloads or promoting publication state.

## Evidence

- Workflow: [29551222886](https://github.com/edithatogo/reimbursement-atlas/actions/runs/29551222886)
- PBS v3 schedules: 10 records, schema pass.
- PBS v3 items: 14,840 records across two CSV pages, schema pass.
- PBS v3 fees: 17 records, schema pass.
- Source validation and source contracts: 2 pass, 7 intentional licence-gated skips, 0 failures.
- Acquisition status: `acquired_unreviewed`; raw responses remain ignored runner/local-cache evidence.

## Boundary

The source-health issue remains open because seven historical MBS/CMS targets require source-specific
licence review. No reviewed-source bundle, OSF registration, Hugging Face publication, Zenodo deposit,
or policy claim was created or promoted.

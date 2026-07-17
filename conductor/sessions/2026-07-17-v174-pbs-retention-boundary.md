# v174 PBS retention boundary and cadence correction

## Objective

Align the PBS source registry with the official monthly distribution cadence and document the
rolling historical-retention boundary before treating historical archiving as an implementation
task.

## Evidence

- Official PBS API documentation: https://data.pbs.gov.au/document/91327.html
- The public data mart retains thirteen months of schedules, including the most recent schedule.
- The registry now records `au_pbs.refresh_cadence: monthly`.
- Regression coverage: `tests/unit/test_registries.py::test_pbs_registry_matches_documented_monthly_refresh`.
- Regenerated source registry, data dictionary, research package, licence queue, seed lake and
  dashboard seed all pass their contracts.

## Boundary

This change documents and tests metadata only. It does not download historical PBS payloads,
extend the API retention window, approve redistribution or change the `acquired_unreviewed`
status of the July 2026 extract. Long-term archiving remains an operational task gated by source
terms and accountable review.

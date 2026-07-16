# v79 publication and historical review automation

## Implemented

- Added a scheduled/manual metadata-only historical MBS inventory refresh workflow.
- Added a manual read-only Zenodo preflight workflow that validates metadata and release gates
  without accepting credentials or performing a deposition.
- Kept historical raw payload acquisition and Zenodo DOI creation fail-closed behind source
  licence, research review and publication approval.
- Added deterministic Conductor issue acceptance criteria for the remaining external work.

## Boundary

These workflows improve repository automation but do not turn external review into a machine
pass. Historical MBS/PBS bundles still require source-specific terms review and a reviewed PBS
extract. Zenodo still requires an approved target, publication decision and future token-gated
deposition implementation.

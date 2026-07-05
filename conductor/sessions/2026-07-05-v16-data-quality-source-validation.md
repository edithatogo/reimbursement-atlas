# Session: v16 data-quality and source validation layer

## Focus

Implemented the next hardening layer after v15: post-download source-content validation, table-level data-quality gates and a research-question linkage matrix.

## Added

- `src/reimburse_atlas/source_validation.py`
- `src/reimburse_atlas/data_quality.py`
- `src/reimburse_atlas/roadmap_linkages.py`
- CLI commands: `source-validation`, `data-quality`, `roadmap-linkages`
- generated dashboard-safe outputs for source validation, data quality and research linkages
- Conductor track `track_data_quality_evidence`
- additional generated GitHub issues covering evidence readiness

## Current caveat

Live downloads remain blocked by sandbox DNS, so source-content validation records show executable public downloads as `missing` until run in a network-enabled environment. This is expected and now visible rather than implicit.

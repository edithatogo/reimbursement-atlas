# Validation evidence

This record concerns implementation and metadata intake. It grants no source
licence, scientific approval, human review or public-product promotion.

## Executed checks

Commands below omit environment-specific executable locations. The isolated
interpreter was Python 3.14.10 and Ruff was 0.16.4. `PYTHONPATH=src` was set for
repository Python entry points. The existing repository dependency lock was not
changed.

| Check | Command or scope | Observed result |
| --- | --- | --- |
| Focused behavior and existing contracts | `python -m pytest tests/unit/test_casemix_handoff.py tests/unit/test_medallion_contracts.py -q` | 39 passed: 34 intake tests and five medallion tests |
| Repository lint | `ruff check .` | Passed |
| Repository formatting | `ruff format --check .` | Passed; 1,181 files already formatted |
| Repository compilation | `python -m compileall -q src scripts tests` | Passed |
| Seed mirror consistency | `python scripts/validate_seed_sync.py` | Passed |
| Existing tracked public-data policy | `python scripts/check_public_data_policy.py` | Passed; this command considers tracked paths |
| Native CLI validation | `python -m reimburse_atlas.cli validate` | Passed; 33 tracks and no dangling source/version references |
| Native data-quality report | `python scripts/make_data_quality_report.py` | 43 checks passed; zero warnings, failures or missing checks |
| Targeted strict typing | `basedpyright` against the two new implementation entry points, with the repository's strict settings and the available isolated environment | Zero errors, warnings or notes; not a full repository type check |
| Receiving CLI | `python scripts/validate_casemix_handoff.py HANDOFF.json` | Synthetic fixture and actual-shaped 243-record/11-candidate handoff accepted as metadata only, all promotions blocked |
| Actual candidate fixity | Independently hashed all eleven candidate files and compared ordered dependency hashes with envelope records | Matched after the producer narrowed source dependencies and removed unsupported passed gates |

The native CLI check used an ephemeral environment with locked Pydantic 2.13.4,
defusedxml 0.7.1 and Typer 0.27.1. The receiving tests used the documented isolated
development environment; they are not claimed to be a full locked-environment CI
run.

The final producer handoff was validated after its code commit, release identity
and generation timestamp were frozen. The exact admission counts, handoff hash
and source commit are recorded in `operational_admission.json`; the full receipt,
envelope and eleven candidate payloads remain outside Git. Candidate file hashes
were checked independently. The bounded receipt does not accept the new source
scope or authorize any product promotion.

## Regenerated projections

The track was registered in `conductor/TRACKS.md`, `conductor/tracks.yml` and the
canonical `conductor_tracks` JSONL seed. These native entry points were executed:

```text
python scripts/sync_seed_csvs.py
python scripts/make_graph_seed.py
python scripts/create_github_project_items.py
python scripts/make_github_project_export.py
python scripts/make_data_quality_report.py
```

The existing `reimburse_atlas.datalake.materialise_seed_lake` builder regenerated
61 tables using locked PyArrow 25.0.1 and DuckDB 1.5.5, preserving Parquet and
DuckDB generation rather than changing optional-format availability. The existing
`scripts/sync_dashboard_seed.py` copied the resulting public metadata projections.
Issue-draft generation produced no changed drafts. No external issue or GitHub
Project was created or modified.

## Exact remaining gate boundary

Eight command equivalents from the 17-entry `quick` profile passed:
`ruff_check`, `ruff_format_check`, `compileall`, `seed_sync`, `public_data_policy`,
`cli_validate`, `github_project_export` and `data_quality`.

The following quick-profile entries were not executed in this bounded pass:

- `protocol_status`
- `source_content_validation`
- `source_contracts`
- `final_handoff`
- `roadmap_linkages`
- `data_dictionary`
- `licence_review_queue`
- `evidence_readiness`
- `source_drift`

`pixi run local-quality-quick` could not start: Pixi was absent from PATH and its
standard user/system installation locations. The official installer HEAD request
returned HTTP 403. `uv sync --locked --all-extras --dry-run` succeeded and reported
129 downloads and 138 package installations; this full API/MCP/data/tooling
bootstrap was not undertaken. Relevant native checks above used bounded
environments instead. Neither the complete quick profile nor the complete CI
profile is represented as passed.

Full-suite coverage, full repository typing, security/package/dashboard checks,
remaining generated-output parity, and hosted protected-branch gates remain
pending before merge. No commit or push is asserted by this record.

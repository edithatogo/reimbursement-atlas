# Session: v5 reviewed source bundles and publication readiness

## Summary

This pass hardened the transition from design fixtures to reviewed live-source validation.

## Added

- Reviewed source bundle workflow in `src/reimburse_atlas/local_sources.py`.
- CLI commands: `validate-seed-files`, `publication-manifest`, `reviewed-source-bundle`, `ontology-seed`.
- Seed JSONL/CSV synchronisation checks in `src/reimburse_atlas/validation.py`.
- Publication-manifest generator in `src/reimburse_atlas/publication.py`.
- Local-only ontology concept seed workflow in `src/reimburse_atlas/terminologies.py`.
- Analysis recipe seeds in `data/seed/analysis_recipes.*`.
- Policy signal matrix output in `data/derived/vertical_slice/policy_signal_matrix.*`.
- Expanded graph nodes/edges to include recipes and synthetic ontology concepts.

## Validation

Local test suite result: `60 passed, 4 skipped`.

## Next work

1. Use a manually downloaded MBS descriptor/item-map file and CMS CLFS file to create reviewed-source bundles.
2. Add source-specific validation assertions for those real files.
3. Add dashboard tables for analysis recipes, ontology concepts and publication-manifest summaries.
4. Add a GitHub Actions job that runs seed sync, public data policy, publication manifest and generated artefact diff checks.

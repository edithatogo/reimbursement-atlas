# OSF Reconciliation

`reimburse_atlas.osf_sync.reconcile_osf_manifest` is the repository-owned
planning boundary for future `osf-cli-go` publication. It compares generated
manifest rows with remote metadata and emits only deterministic actions:

- `blocked` for rows without explicit publication approval or without a local file;
- `create` for an approved local path absent remotely;
- `update` for checksum or size drift;
- `skip` when checksum and size match;
- `delete` only for explicitly managed remote rows when `prune=True`.

The planner performs no network IO and cannot upload, delete, or alter OSF
content. A future CLI adapter must consume this plan, preserve dry-run mode,
respect protocol/licence/data-quality gates, and require explicit approval for
mutation and pruning. The current CI workflow remains fail-closed because no
manifest row is publication-approved.

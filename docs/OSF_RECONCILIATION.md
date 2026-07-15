# OSF Reconciliation

GitHub issue [#134](https://github.com/edithatogo/reimbursement-atlas/issues/134)
tracks the manifest-driven synchronization adapter. The repository-owned
`reimburse_atlas.osf_sync.reconcile_osf_manifest` is the planning boundary for
future `osf-cli-go` publication. It compares generated
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

## Local dry-run command

The planner is exposed through the CLI so a credentialed adapter can be tested
without granting it mutation authority:

```bash
PYTHONPATH=src reimbursement-atlas osf-reconcile \
  --manifest-path data/derived/osf/sync_manifest.jsonl \
  --remote-state-path /path/to/exported_osf_state.json \
  --output-path data/derived/osf/reconciliation_report.json
```

The remote-state file is an exported JSON array containing `osf_path`,
`sha256`, `byte_size`, and optional `managed_by_manifest` fields. The command
always reports `network_io: false` and `mutation_performed: false`. `--prune`
only plans deletion of remote rows explicitly marked as managed; it never
deletes by default. The report is deterministic for identical local and
remote snapshots and is suitable as the input contract for a future
`osf-cli-go` adapter.

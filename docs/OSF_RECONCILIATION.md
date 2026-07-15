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

## Registration lifecycle and drift check

GitHub issue [#135](https://github.com/edithatogo/reimbursement-atlas/issues/135)
tracks registration lifecycle verification. The OSF plan now generates
`data/derived/osf/registration_freeze.json`, containing deterministic protocol
and manifest fingerprints. A credentialed adapter can export registration
metadata and check it without network IO or mutation:

```bash
PYTHONPATH=src reimbursement-atlas osf-registration-check \
  --remote-state-path /path/to/registration_snapshot.json \
  --output-path data/derived/osf/registration_check.json
```

The command reports `blocked` when review or an active remote registration is
missing, `drift` when protocol or manifest fingerprints differ, and `ready`
only when the snapshot matches and `review_approved` is explicitly true. The
generated freeze is intentionally unapproved and therefore remains fail-closed
until human methods, domain, licence and governance review is recorded.

The same plan generates `data/derived/osf/registration_review_packet.md`. This is a
deterministic, non-mutating review aid containing the freeze digests, protocol/report
completeness, blocked manifest-row count and blank approval fields. It must be completed
by an accountable human reviewer; generation never changes `review_approved` or
`publish_allowed`.

# Mapping accountable approval boundary

The active `expansion_v9` mapping cycle has a checksum-bound owner packet at
`data/derived/mapping_study/expansion_v9/adjudication_owner_packet.json`.
It contains 1,500 proposed decisions, zero family quota gaps and proposal
SHA-256:

```text
dd45a5f8a94d6e050e67c4ee88226104a4e599e8dcd016822e0e9ab7f3830ef5
```

The repository cannot infer accountable approval from generated packets or
agent review. The recommended decision is to approve this exact proposal using
the existing fail-closed command:

```bash
PYTHONPATH=src python scripts/approve_mapping_adjudication.py \
  --cycle expansion_v9 \
  --proposal-sha256 dd45a5f8a94d6e050e67c4ee88226104a4e599e8dcd016822e0e9ab7f3830ef5 \
  --reviewer ACCOUNTABLE_OWNER \
  --confirm APPROVE_MAPPING_ADJUDICATION:dd45a5f8a94d6e050e67c4ee88226104a4e599e8dcd016822e0e9ab7f3830ef5 \
  --approved-at 2026-08-01T00:00:00Z
```

Replace only `ACCOUNTABLE_OWNER` and the approval timestamp. Option B is to
reject the proposal and create a new immutable cycle. Option C is to leave the
cycle pending; this is the current fail-closed state and permits no broad
mapping-performance claim.

# Implementation plan

- [x] HF-01: Validate the candidate bundle and publication gates.
- [x] HF-02: Reconcile destination dataset and Space metadata.
- [x] HF-03: Publish the governed dataset and static Space with an ephemeral
  authenticated CLI session.
- [x] HF-04: Verify remote identity, metadata and commit parity.
- [x] Review Fixes: Reconcile canonical backlog labels and generated issue/Project
  statuses for completed HF publication tasks.
- [x] HF-05: Regenerate final handoff and archive after dependent external states
  settle. The dataset and Space are published with remote parity verified, and
  the final handoff records `publication_remote_parity_verified`.

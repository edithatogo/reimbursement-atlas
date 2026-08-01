# Policy demonstrator blocker plan

The repository-owned generation path is complete for five protocolled claim
packages, but release claims remain gated.

## Sequence

1. Freeze the reviewed-derived inputs, source versions, permitted fields,
   denominators, exclusions and transformation checksums for each question.
2. Re-run the claim-package and evidence-readiness generators after any input
   change; deterministic output is required.
3. Record scoped accountable review against each exact package checksum.
4. Regenerate evidence, dashboard and release artefacts only after the scoped
   decisions pass.

## Options

- **Recommended:** approve each current checksum-bound package within its
  stated scope. This closes the review gate without authorizing causal,
  universal-coverage, net-price, paper or preprint claims.
- Reject a package and create a new immutable analysis cycle when its inputs or
  estimand are not acceptable.
- Leave packages pending. This is the current fail-closed state and permits
  descriptive demonstrator output only.

The repository cannot infer accountable approval from a generated report or
from local tests.

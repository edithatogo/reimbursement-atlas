# Remaining Blocker Closure Plan

Status: `in_progress`
Recorded: 2026-08-03
Track: `track_release_gate_reconciliation_closeout`

This plan is the canonical dependency map for the remaining release blockers. It
separates repository-owned work from external source, accountable-review and
publication decisions. No downstream publication gate may be inferred from a
passing repository gate.

## Decision Matrix

### Dashboard evidence (#493)

| Option | Trade-off | Decision |
| --- | --- | --- |
| A. Re-run the full browser workflow at current `main` and regenerate the packet | Highest assurance; requires CI/browser runtime | **Recommended** |
| B. Reuse the prior packet and document the commit mismatch | Fast, but invalidates displayed-data parity | Rejected |
| C. Mark the packet approved without a current-head artifact | Unverifiable and not reproducible | Rejected |

Contingency: if browser artifacts cannot be produced, keep the gate blocked and
record the exact missing artifact, tested commit and failed parity assertion.
After a fresh packet exists, the accountable owner must approve the exact
automated and owner packet hashes within the declared scope.

### Mapping counterparts (#490)

| Option | Trade-off | Decision |
| --- | --- | --- |
| A. Rights-cleared derived bundles with source/version/licence/checksum receipts | Supports reproducible publication and evaluation | **Recommended** |
| B. Metadata-only adapters with local raw acquisition instructions | Preserves provenance but cannot satisfy a public derived-case quota | Fallback |
| C. Fixtures or unreviewed public text | Permits testing but cannot support evidence claims | Rejected |

Contingency: retain #490 blocked by source family and quota when terms or
payloads are unavailable. Never promote restricted descriptors or raw payloads.

### Blinded adjudication and holdout (#491)

| Option | Trade-off | Decision |
| --- | --- | --- |
| A. Two isolated review passes, deterministic adjudication, one untouched holdout | Strongest independence and auditability; requires complete frame | **Recommended** |
| B. Single-pass owner labels | Faster, but cannot establish blinded reliability | Rejected for evidence claims |
| C. Synthetic or fixture-only evaluation | Useful for contract tests only | Rejected for atlas performance |

Contingency: fail closed if the 1,500-row frame, 600-case development set,
150-case holdout, reviewer separation, or provenance checks are incomplete.

### Hugging Face publication (#534)

| Option | Trade-off | Decision |
| --- | --- | --- |
| A. Keep dry-run and metadata validation only until `evidence_release_ready=true` | Prevents unsupported public claims | **Recommended** |
| B. Publish metadata-only documentation | Limited utility and may imply readiness | Only if separately approved and clearly labelled |
| C. Publish the dataset while evidence gates are false | Irreversible public-state risk | Rejected |

Contingency: credentials may be configured and validated without dispatching a
mutation. No token is written to the repository or logs.

### Local `main` reconciliation

| Option | Trade-off | Decision |
| --- | --- | --- |
| A. Preserve the pre-squash local commit on a named recovery ref, then align local `main` to `origin/main` | Clean working state while retaining recovery | **Recommended** |
| B. Merge the pre-squash commit into local `main` | Preserves history but creates a redundant local merge | Not preferred |
| C. Delete or reset without a recovery ref | Simple but destructive | Rejected |

The recovery ref must be retained until the aligned local `main` has been
verified, then removed only after an explicit clean-up check.

## Dependency Sequence

1. Merge and verify the repository-owned Conductor plan and gate contracts.
2. Reconcile local `main` non-destructively after the protected merge.
3. Generate a current-head dashboard browser packet and await scoped owner approval.
4. Acquire and licence-review all counterpart families required by #490.
5. Freeze the checksum-bound candidate frame.
6. Run isolated reviews, adjudication, development tuning and one-time holdout evaluation for #491.
7. Regenerate evidence, release, policy, publication and handoff projections.
8. Re-run Hugging Face dry-run validation; dispatch publication only when all independent gates pass.
9. Preserve Zenodo as published and perform final archive/handoff regeneration.

## Acceptance Contract

- Every blocker has an evidence-derived status and stable reason code.
- Current-head dashboard evidence has matching commit, source fingerprint and data fingerprint.
- #490 contains real reviewed derived counterparts, not fixtures or raw restricted payloads.
- #491 contains disjoint, checksum-bound development and untouched holdout sets with complete review provenance.
- Hugging Face publication remains fail-closed while `evidence_release_ready=false`.
- Local `main` exactly matches `origin/main` after recovery preservation and verification.
- Papers and preprints remain excluded from all publication manifests and workflows.

# Claim-package gate reconciliation

## Scope

Correct the evidence-readiness promotion path, reconcile current release
documentation, and close GitHub issues whose implementation criteria are already
verified.

## Result

- Evidence scores can establish prototype maturity but cannot independently
  produce `evidence_ready`.
- The optional research-claim decision contract binds a permitted derived claim
  package to its current SHA-256 and requires reviewed inputs, validated analysis,
  scoped approval and an accountable review record.
- Current status remains `repository_release_ready=true`,
  `evidence_release_ready=false`, `policy_claims_ready=false` and
  `osf_registration_ready=false`.
- GitHub issue #585 tracks the implemented claim contract. Issue #586 tracks the
  five real analyses and bounded reviews still required.
- Completed implementation issues #501, #565-#579 and #584 were closed. Their
  downstream external or evidence dependencies remain open under #511, #532 and
  #586.

## Boundary

Registration `gqk4z` remains externally pending OSF approval. Policy demonstrators
remain fixtures, not evidence. Zenodo/DataCite publication is not authorized until
OSF and evidence gates pass. Papers and preprints remain excluded.

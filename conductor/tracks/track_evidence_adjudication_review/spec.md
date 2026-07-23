# Specification

## Overview

Close the remaining human-review boundaries without overstating evidence. The
accountable reviewer is the repository owner; every decision must identify the
scope, artefact/checksum, review method and resulting limitation.

## Requirements

- Build and review the stratified 750-case mapping pack with blinded dual review and holdout evaluation.
- Adjudicate positive and negative controls, preserving false-positive boundaries.
- Record CMS AMA/CPT, MBS/PBS reuse and historical-source decisions separately.
- Review dashboard visual/accessibility evidence within its tested browser scope.
- Keep prototype results distinct from evidence-ready or policy-ready claims.
- Keep reviewers blind to the other pass and to development/holdout assignment; freeze labels
  before deterministic splitting and make the one-time holdout fingerprint immutable.
- Report exact binomial intervals and family-specific denominators/exclusions; never generalise a
  completed stratum to unsupported atlas-wide performance.

## Acceptance criteria

- [ ] Mapping review packet, reviewer decisions and holdout results are checksum-bound.
- [ ] Source licence decisions identify permitted fields and excluded payloads/descriptors.
- [ ] Dashboard review records viewport/browser scope and unresolved accessibility limitations.
- [ ] Evidence-readiness output changes only when its acceptance criteria are met.
- [ ] Final handoff lists no silently resolved review blockers.
- [ ] Candidate-frame quotas, review independence, split disjointness and holdout one-time use are
  machine-validated and fail closed.

## External gates

- Accountable domain/research review.
- Human visual/accessibility review.
- Source-rights decisions for restricted families.

## Authoritative inputs

- `docs/MAPPING_CALIBRATION_PROTOCOL.md`
- `docs/RESEARCH_PROTOCOL_REVIEW_CHECKLIST.md`
- `data/mapping_review/decisions.jsonl`
- `data/derived/evidence_readiness/`
- `data/derived/final_handoff/`

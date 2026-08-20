# Risk-tiered approval friction reduction

## Overview

Reduce repetitive approval requests while preserving the repository's fail-closed rights,
research and publication boundaries.

## Requirements

- Classify deterministic project-owned control artefacts under Apache-2.0 without source-rights
  review.
- Reuse bounded dashboard approval only when historical packet integrity, UI fingerprint, routes,
  browser scope and current machine evidence all pass.
- Require accountable review for material rights, claim, interface-scope and protocol changes.
- Keep external publication mutations separately authorized.
- Expose stable approval requirements, reason codes and reapproval triggers in generated manifests.

## Acceptance criteria

- [x] Architecture and SBOM artefacts do not enter the licence-review queue.
- [x] Source-derived candidates remain checksum-bound and fail closed.
- [x] Dashboard data-only regeneration can use an integrity-checked standing scoped approval.
- [x] Dashboard UI or review-scope changes invalidate standing approval.
- [x] Targeted, deterministic-generation and repository quality gates pass.
- [ ] GitHub issue #708 and generated Conductor/GitHub Project state are synchronized.

## External gates

No external mutation is part of this track. Existing publication, registration and source-rights
gates remain independent.

## Authoritative inputs

- `docs/APPROVAL_POLICY.md`
- `src/reimburse_atlas/publication.py`
- `src/reimburse_atlas/dashboard_review.py`
- GitHub issue #708

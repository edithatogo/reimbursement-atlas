# 2026-07-16 v25 — Merged release and recommendation closeout

## Scope

Audit and close out the repository-controlled recommendations after the reviewed live-source
provenance change was merged.

## Evidence

- Main commit: `38a399073ef4bc5ae6106c05a3b719d32790b361`.
- PR #176 merged with all required checks green.
- Release-readiness: 35/35 gates pass; `repository_release_ready=true`.
- Source validation, source contracts, data quality, publication manifest, data dictionary,
  research package, HF bundle validation, citation validation and public-data policy pass.
- July 2026 MBS TXT pair: 14,856 derived rows; raw payloads remain ignored and are not tracked.
- GitHub Pages is deployed; source-health/source-drift and stack-canary monitoring are scheduled.
- OSF and Hugging Face mutation paths remain token-gated and fail closed.

## Decision

Repository-controlled recommendations are complete. The remaining work is explicitly review-
gated: MBS/CMS/PBS licensing, mapping adjudication, OSF protocol approval/registration, HF
publication approval, cross-platform visual review and Zenodo deposition.

## Safety boundary

No generated gate may be changed to evidence-ready, policy-ready or published solely because
the software gates pass. Human decisions must be recorded in `docs/REVIEW_DECISIONS.md` before
the corresponding remote mutation or public claim is permitted.

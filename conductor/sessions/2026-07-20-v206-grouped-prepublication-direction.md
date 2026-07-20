# Session v206: Grouped pre-publication direction

## Owner direction

On 2026-07-20 the repository owner approved Groups A-D from the pre-publication decision
briefing. The approval authorises repository-owned preparation and validation only.

## Implemented scope

- Group A: metadata-first historical MBS/PBS inventory and local-cache acquisition; CMS CLFS
  derived numeric/payment fields and source metadata only; no raw restricted payloads or CPT/HCPCS
  descriptors.
- Group B: conservative mapping review remains active; the four-case fixture remains smoke-only,
  negative controls remain visible, and the 750-case blinded dual-review/holdout protocol remains
  required.
- Group C: retain the tested dashboard browser/device baseline as scoped regression evidence; no
  universal WCAG conformance claim is made.
- Group D: regenerate and validate local OSF and Hugging Face candidate packages without remote
  upload, registration, publication or metadata correction.

## Explicitly not authorised

Paper, preprint, manuscript and other publication submission; OSF registration or upload; Hugging
Face remote mutation; source-rights assertions beyond the documented field scope; policy claims;
and evidence-readiness promotion.

## Validation record

Run `pixi run osf-plan`, `pixi run hf-bundle`, `pixi run hf-destination`, dashboard validation,
source validation, source contracts, data quality, release readiness and final handoff after
regeneration. Preserve any blocked-review status in generated outputs.

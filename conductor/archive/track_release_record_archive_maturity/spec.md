# Specification

## Overview

Align GitHub, OSF, Hugging Face, dashboard, citation and archive records into one
versioned public-product record. The track may prepare and validate release assets,
but publication, signing, DOI minting and paper submission remain explicit gates.

## Requirements

- Keep `CITATION.cff`, README, package metadata, dashboard status and OSF metadata aligned.
- Produce a signed/attested archive only after evidence and source-rights gates pass.
- Make dashboard routes, accessibility evidence and provenance links citable.
- Keep Hugging Face metadata and destination reports synchronized without raw-source upload.
- Record release blockers, external approvals and exact commit/archive checksums.
- Use one Zenodo concept record with immutable version records; reserve a version DOI only after
  the exact release file inventory is frozen. Keep that release immutable: record the reserved DOI
  in Zenodo metadata and the external receipt, then add the concept DOI to `CITATION.cff` in the
  subsequent commit/release rather than rebuilding already frozen assets.
- Keep software licensing, source-data rights and paper/preprint publication as separate fields
  and gates.

## Acceptance criteria

- [x] Citation and README identify the current product, scope, limitations and citation method.
- [x] Dashboard visual/accessibility review evidence is linked and scoped.
- [x] OSF and Hugging Face records expose consistent project identity and licence boundaries.
- [ ] Archive manifest, SBOM, provenance and attestations are reproducible.
- [ ] Public release remains blocked until evidence, rights and registration gates pass.
- [x] Zenodo draft and DataCite metadata validate without network mutation; publication requires
  explicit environment authorization and post-publication DOI-resolution evidence.

## Authoritative inputs

- `CITATION.cff`
- `README.md`
- `docs/RELEASE_READINESS.md`
- `docs/DASHBOARD_VALIDATION.md`
- `data/derived/release_readiness/`
- `data/derived/publication/`

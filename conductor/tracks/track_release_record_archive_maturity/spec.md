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
- Use one Zenodo concept record with immutable version records; reserve a DOI only after the exact
  release file inventory is frozen and regenerate citation metadata before publication.
- Keep software licensing, source-data rights and paper/preprint publication as separate fields
  and gates.

## Acceptance criteria

- [ ] Citation and README identify the current product, scope, limitations and citation method.
- [ ] Dashboard visual/accessibility review evidence is linked and scoped.
- [ ] OSF and Hugging Face records expose consistent project identity and licence boundaries.
- [ ] Archive manifest, SBOM, provenance and attestations are reproducible.
- [ ] Public release remains blocked until evidence, rights and registration gates pass.
- [ ] Zenodo draft and DataCite metadata validate without network mutation; publication requires
  explicit environment authorization and post-publication DOI-resolution evidence.

## Authoritative inputs

- `CITATION.cff`
- `README.md`
- `docs/RELEASE_READINESS.md`
- `docs/DASHBOARD_VALIDATION.md`
- `data/derived/release_readiness/`
- `data/derived/publication/`
